"""Native engine -> watcher -> real MCP stdio -> selected export in owned fixtures.

This is source-build integration evidence, not an installed release or native
assistant selection evaluation. No user repository, service or credentials are changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
import time


def server(args):
    sys.path.insert(0, str(args.mcp_root / "src"))
    import anyio
    from axiom_mcp import security, stdio
    from axiom_mcp.query.cursor import CursorStore
    from axiom_mcp.registry import load_registry
    from axiom_mcp.runtime import Runtime, compose

    registry = load_registry(args.registry, env={"AXIOM_HOME": os.environ["AXIOM_HOME"]}, platform=sys.platform)
    tokens = security.TokenRegistry()
    # Ephemeral fixture credential remains in process environment, never an artifact.
    os.environ["AXIOM_WORKFLOW_READ"] = "workflow-fixture-only"
    reference = {"kind": "env", "variable": "AXIOM_WORKFLOW_READ"}
    tokens.register(security.EnvTokenReference("AXIOM_WORKFLOW_READ"),
                    security.ScopedToken("workflow-read", security.MCP_AUDIENCE,
                                         frozenset({security.CAPABILITY_READ}), frozenset({"workflow"})))
    if not args.denied:
        os.environ["AXIOM_MCP_TOKEN_REFERENCE"] = json.dumps(reference)
    else:
        os.environ.pop("AXIOM_MCP_TOKEN_REFERENCE", None)
    runtime = Runtime(registry, tokens, None, CursorStore())
    composed = compose(stdio.build_stdio_server("workflow-fixture"), runtime, transport="stdio")
    return anyio.run(lambda: stdio.serve_stdio(composed))


async def mcp_checks(args, registry, home, log, denied=False):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    import jsonschema

    argv = [str(Path(__file__).resolve()), "--server", "--mcp-root", str(args.mcp_root), "--registry", str(registry)]
    if denied:
        argv.append("--denied")
    parameters = StdioServerParameters(command=sys.executable, args=argv,
                                       env=dict(os.environ, AXIOM_HOME=str(home), PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1"))
    with log.open("w", encoding="utf-8") as errors:
        async with stdio_client(parameters, errlog=errors) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = {tool.name: tool for tool in (await session.list_tools()).tools}
                assert "graph_query" in tools and "graph_status" in tools
                trace = []
                async def call(name, arguments, expected_error=False):
                    jsonschema.validate(arguments, tools[name].inputSchema)
                    result = await session.call_tool(name, arguments)
                    payload = result.structuredContent
                    if payload is None:
                        payload = {"text": [c.text for c in result.content if hasattr(c, "text")]}
                    trace.append({"tool": name, "arguments": arguments, "is_error": result.isError,
                                  "nodes": len(payload.get("nodes", [])), "generation": payload.get("catalog_generation_id"),
                                  "error": payload.get("code")})
                    assert bool(result.isError) == expected_error, payload
                    return payload
                if denied:
                    await call("graph_status", {"solution_id": "workflow"}, True)
                    return {"discovered_without_read_auth": True, "auth_refused": True, "trace": trace}
                status = await call("graph_status", {"solution_id": "workflow"})
                search = await call("graph_query", {"solution_id": "workflow", "operation": "search", "query": "PingPong",
                                                   "max_nodes": 20, "max_bytes": 8192, "consistency": "allow_stale"})
                candidates = search["nodes"]
                assert len(candidates) >= 2, "duplicate method candidates must not be hidden"
                chosen = next(node for node in candidates if "Demo" in json.dumps(node))
                target = chosen["id"]
                context = await call("graph_query", {"solution_id": "workflow", "operation": "context", "target": target,
                                                     "projection": ["identity", "relations", "source_locations", "coverage"],
                                                     "depth": 1, "max_nodes": 20, "max_edges": 40, "max_bytes": 8192,
                                                     "consistency": "allow_stale"})
                assert "source" in json.dumps(context)
                for node in context.get("nodes", []):
                    location = node["source"]
                    file = args.fixture_repo / location["file"]
                    assert file.is_file(), "MCP source location must resolve from the bound repository"
                    lines = file.read_text().splitlines()
                    assert 1 <= location["start_line"] <= location["end_line"] <= len(lines)
                    assert node["name"] in "\n".join(lines[location["start_line"] - 1:location["end_line"]])
                removal = await call("graph_query", {"solution_id": "workflow", "operation": "search", "query": "RemoveFilesAsync",
                                                     "max_nodes": 20, "max_bytes": 8192, "consistency": "allow_stale"})
                method = removal["nodes"][0]["id"]
                impact = await call("graph_query", {"solution_id": "workflow", "operation": "impact", "target": method,
                                                    "projection": ["identity", "relations", "source_locations", "coverage"],
                                                    "depth": 1, "max_nodes": 20, "max_edges": 40, "max_bytes": 8192,
                                                    "consistency": "allow_stale"})
                await call("graph_query", {"solution_id": "workflow", "operation": "search", "query": "PingPong", "consistency": "require_fresh"}, True)
                await call("graph_job", {"job_id": "fixture-job"}, True)
                return {"transport": "real-sdk-stdio", "discovered_tools": sorted(tools), "candidate_count": len(candidates),
                        "catalog_generation_id": search["catalog_generation_id"],
                        "project_generations": search["project_generations"],
                        "resolved_target": target, "removal_target": method, "source_ranges_returned": True,
                        "source_ranges_validated_against_repository": True,
                        "read_only_escalation_refused": True, "status_observed": bool(status),
                        "impact_nodes": len(impact.get("nodes", [])), "empty_impact_is_safe_to_delete": False, "trace": trace}


def verify(args):
    import anyio
    import jsonschema
    from referencing import Registry, Resource
    daemon = args.daemon.resolve(strict=True)
    args.mcp_root = args.mcp_root.resolve(strict=True)
    schemas = args.mcp_root.parent / "axiom-specs/contracts/schemas"
    schema_registry = Registry().with_resources(
        (p.as_uri(), Resource.from_contents(json.loads(p.read_text(encoding="utf-8")) | {"$id": p.as_uri()}))
        for p in schemas.glob("*.schema.json")
    )
    export_schema_path = schemas / "graph-export.schema.json"
    export_schema = json.loads(export_schema_path.read_text()) | {"$id": export_schema_path.as_uri()}
    cycle_schema = json.loads((schemas / "work-cycle.schema.json").read_text())
    calls = []
    with tempfile.TemporaryDirectory(prefix="axiom workflow ") as temporary:
        root = Path(temporary); repo = root / "repo"; home = root / "home"
        source = repo / "src/Example.cs"; source.parent.mkdir(parents=True)
        source.write_text('namespace Example;\npublic class Demo {\n public void PingPong() {\n  RemoveFilesAsync();\n }\n public void RemoveFilesAsync() {}\n}\n')
        other = repo / "src/Other.cs"
        other.write_text('namespace Example;\npublic class Other {\n public void PingPong() {}\n}\n')
        human = b"# Human instructions\nKeep this file.\n"; (repo / "AGENTS.md").write_bytes(human)
        config = root / "solution.json"; bindings = root / "bindings.json"
        config.write_text(json.dumps({"id": "workflow", "profile": "default", "catalog_host_repo": "primary",
                                      "projects": [{"id": "app", "repo_id": "primary", "path": "src"}]}))
        bindings.write_text(json.dumps({"bindings": {"primary": str(repo)}}))
        env = dict(os.environ, AXIOM_HOME=str(home))
        def call(*words, failed=False):
            result = subprocess.run([str(daemon), *map(str, words), "--json"], env=env, capture_output=True, text=True, timeout=45)
            calls.append({"argv": [str(w) if not str(w).startswith(str(root)) else "<fixture-input>" for w in words], "exit_code": result.returncode})
            assert (result.returncode != 0) == failed, result.stdout + result.stderr
            return json.loads(result.stdout), result.stderr
        call("solution", "register", "--config", config, "--bindings", bindings, "--dry-run")
        call("solution", "register", "--config", config, "--bindings", bindings, "--apply")
        first, _ = call("build", "--solution", "workflow")
        second, _ = call("build", "--solution", "workflow")
        assert first["cycle"]["generation_after"] == second["cycle"]["generation_after"]
        assert second["published_generations"] == 0
        full, _ = call("build", "--solution", "workflow", "--full")
        assert full["cycle"]["files_analyzed"] >= 2
        registry = root / "mcp-registry.json"
        registry.write_text(json.dumps({"schema_version": 1, "axiom_home": str(home), "instances": [{"instance_id": "local-instance"}],
            "solutions": [{"solution_id": "workflow", "instance_id": "local-instance", "catalog_host_repo": "primary",
                            "repositories": [{"repo_id": "primary", "repo_root": str(repo), "projects": [{"project_id": "app"}]}]}]}))
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        args.fixture_repo = repo
        mcp = anyio.run(mcp_checks, args, registry, home, root / "mcp.log")
        denied = anyio.run(mcp_checks, args, registry, home, root / "denied.log", True)
        assert source_hash == hashlib.sha256(source.read_bytes()).hexdigest(), "impact must not delete/edit source"
        out = root / "selected"
        selected_generation = next(row["generation_id"] for row in mcp["project_generations"] if row["project_id"] == "app")
        receipt, _ = call("export", "--solution", "workflow", "--project", "app", "--node-id", mcp["resolved_target"],
                          "--exact-projection", "--project-generation", "app=" + selected_generation, "--out", out)
        artifact = json.loads((out / "graph.json").read_text())
        jsonschema.Draft202012Validator(export_schema, registry=schema_registry).validate(artifact)
        assert artifact["completeness"] == "filtered_projection"
        assert receipt["generation_vector"]["app"] == selected_generation
        assert not artifact["projects"][0]["edges"]
        assert [node["id"] for p in artifact["projects"] for node in p["nodes"]] == [mcp["resolved_target"]]
        saved = (out / "graph.json").read_bytes(); call("export", "--solution", "workflow", "--out", out, failed=True)
        assert (out / "graph.json").read_bytes() == saved
        pointer = repo / ".axiom/graph/workflow/_catalog/live/current.json"
        def generation(): return json.loads(pointer.read_text())["generation_id"]
        changes = []
        with (root / "watch.log").open("w", encoding="utf-8") as errors:
            proc = subprocess.Popen([str(daemon), "watch", "--json"], env=env, stdout=subprocess.PIPE, stderr=errors,
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
            try:
                time.sleep(1)
                assert proc.poll() is None
                failed, stderr = call("build", "--solution", "workflow", failed=True)
                assert failed["code"] == "WRITER_ALREADY_RUNNING" and '"status":"failed"' in stderr
                for operation in ("save", "rename", "delete", "delete_last"):
                    before = generation(); start = time.monotonic()
                    if operation == "save": source.write_text(source.read_text() + "public class AfterSave {}\n")
                    elif operation == "rename": source.rename(source.with_name("Renamed.cs"))
                    elif operation == "delete": source.with_name("Renamed.cs").unlink()
                    else: other.unlink()
                    deadline = start + 20
                    while time.monotonic() < deadline and generation() == before:
                        assert proc.poll() is None, (root / "watch.log").read_text()[-2000:]
                        time.sleep(.1)
                    assert generation() != before, operation + " did not publish automatically"
                    # Export during live publication uses only the pinned vector.
                    changed_out = root / operation
                    snapshot, _ = call("export", "--solution", "workflow", "--out", changed_out)
                    changed = json.loads((changed_out / "graph.json").read_text())
                    jsonschema.Draft202012Validator(export_schema, registry=schema_registry).validate(changed)
                    current_nodes = changed["projects"][0]["nodes"]
                    if operation == "delete": assert not any("Demo" in json.dumps(n) or "AfterSave" in json.dumps(n) for n in current_nodes)
                    if operation == "delete_last": assert not current_nodes and not changed["projects"][0]["edges"]
                    changes.append({"operation": operation, "before": before, "after": generation(), "client_observed_seconds": time.monotonic() - start,
                                    "export_catalog": snapshot["catalog_generation_id"]})
                before_invalid = generation()
                log_before_invalid = len((root / "watch.log").read_text())
                source.write_text("namespace Example;\npublic class Broken {\n")
                deadline = time.monotonic() + 10
                while '"status":"failed"' not in (root / "watch.log").read_text()[log_before_invalid:]:
                    assert proc.poll() is None
                    assert time.monotonic() < deadline, (root / "watch.log").read_text()[-3000:]
                    time.sleep(.1)
                assert generation() == before_invalid and proc.poll() is None
                source.write_text("namespace Example;\npublic class RecoveredSource {}\n")
                deadline = time.monotonic() + 15
                while generation() == before_invalid:
                    assert proc.poll() is None and time.monotonic() < deadline
                    time.sleep(.1)
                changes.append({"operation":"malformed_save_recovery","before":before_invalid,"after":generation(),"writer_preserved":True})
            finally:
                if proc.poll() is None: proc.send_signal(signal.CTRL_BREAK_EVENT if os.name == "nt" else signal.SIGINT)
                stdout, _ = proc.communicate(timeout=15)
                assert proc.returncode == 0, (root / "watch.log").read_text()[-2000:]
                json.loads(stdout)
        events = [json.loads(line)["cycle"] for line in (root / "watch.log").read_text().splitlines()
                  if line.startswith('{') and json.loads(line).get("target") == "work_cycle"]
        assert len(events) >= 3
        assert all(isinstance(c["processing_ms"], int) and c["processing_ms"] >= 0 for c in events)
        for cycle in [first["cycle"], second["cycle"], full["cycle"], *events]:
            jsonschema.validate(cycle, cycle_schema)
        assert (repo / "AGENTS.md").read_bytes() == human
        # A malformed source must fail without advancing the valid catalog pointer.
        before_bad = generation()
        source.write_text("namespace Example;\npublic class Broken {\n")
        bad, failed_stderr = call("build", "--solution", "workflow", failed=True)
        assert bad["code"] == "VALIDATION_ERROR" and generation() == before_bad
        assert '"status":"failed"' in failed_stderr
        failed_cycles = [json.loads(line)["cycle"] for line in failed_stderr.splitlines()
                         if line.startswith('{') and json.loads(line).get("target") == "work_cycle"]
        assert failed_cycles and failed_cycles[0]["status"] == "failed"
        for cycle in failed_cycles: jsonschema.validate(cycle, cycle_schema)
        source.unlink()
        (repo / "src/unknown.py").write_text("def unsupported_language(): pass\n")
        unsupported, _ = call("build", "--solution", "workflow")
        assert unsupported["cycle"]["status"] == "partial", unsupported["cycle"]
        return {"scope": "native-source-build-integration", "platform": platform.system(), "machine": platform.machine(),
                "engine_sha256": hashlib.sha256(daemon.read_bytes()).hexdigest(), "build": first["cycle"], "noop": second["cycle"],
                "full": full["cycle"], "mcp": mcp, "denied_mcp": denied, "selected_export": receipt,
                "failed_cycles": failed_cycles, "unsupported_cycle": unsupported["cycle"],
                "watch_changes": changes, "watch_cycles": events, "manual_reconcile_after_change": False,
                "require_fresh_during_watch": False, "writer_collision_refused": True, "source_impact_preserved": True,
                "human_file_preserved": True, "malformed_source_refused": True,
                "watcher_recovers_after_malformed_save": True,
                "unsupported_language_partial": True, "native_host_selection": "separate_evaluation", "calls": calls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daemon", type=Path); parser.add_argument("--mcp-root", type=Path, required=True)
    parser.add_argument("--registry", type=Path); parser.add_argument("--out", type=Path)
    parser.add_argument("--server", action="store_true"); parser.add_argument("--denied", action="store_true")
    args = parser.parse_args()
    if args.server: return server(args)
    report = verify(args); args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("PASS native build/noop/full/watch-save-rename-delete/MCP/selected-export boundaries")


if __name__ == "__main__": main()
