"""One native Codex workflow evaluation with real scoped MCP and an owned fixture.

This runs a host model turn only when explicitly invoked. It never installs a
plugin, changes user configuration or supplies the expected analysis to the host.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


async def discovered_schemas(argv, env, log):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    with log.open("w", encoding="utf-8") as errors:
        async with stdio_client(StdioServerParameters(command=shutil.which("python"), args=argv, env=env), errlog=errors) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return [tool.model_dump(mode="json") for tool in (await session.list_tools()).tools]

ROOT = Path(__file__).resolve().parents[1]


def verify(args):
    with tempfile.TemporaryDirectory(prefix="axiom host eval ") as temporary:
        root = Path(temporary); repo = root / "repo"; home = root / "home"
        source = repo / "src/Example.cs"; source.parent.mkdir(parents=True)
        source.write_text("namespace Example;\npublic class Demo {\n public void PingPong() {\n  RemoveFilesAsync();\n }\n public void RemoveFilesAsync() {}\n}\n")
        shutil.copytree(ROOT / "skills", repo / ".agents/skills")
        config = root / "solution.json"; bindings = root / "bindings.json"
        config.write_text(json.dumps({"id": "workflow", "profile": "default", "catalog_host_repo": "primary",
                                     "projects": [{"id": "app", "repo_id": "primary", "path": "src"}]}))
        bindings.write_text(json.dumps({"bindings": {"primary": str(repo)}}))
        env = dict(os.environ, AXIOM_HOME=str(home), PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
        for words in [["solution", "register", "--config", str(config), "--bindings", str(bindings), "--apply"],
                      ["build", "--solution", "workflow"]]:
            result = subprocess.run([str(args.daemon.resolve()), *words, "--json"], env=env, capture_output=True, text=True, timeout=45)
            if result.returncode: raise RuntimeError(result.stdout + result.stderr)
        registry = root / "registry.json"
        registry.write_text(json.dumps({"schema_version": 1, "axiom_home": str(home), "instances": [{"instance_id": "local-instance"}],
            "solutions": [{"solution_id": "workflow", "instance_id": "local-instance", "catalog_host_repo": "primary",
                            "repositories": [{"repo_id": "primary", "repo_root": str(repo), "projects": [{"project_id": "app"}]}]}]}))
        mcp_args = [str(ROOT / "tests/verify_workflow_runtime.py"), "--server", "--mcp-root", str(args.mcp_root.resolve()), "--registry", str(registry)]
        prompt = "Use $axge to complete this request: impact remove method RemoveFilesAsync on this project."
        # Supplied editor/registry context is ordinary input, not a policy workaround.
        # These are raw fixture artifacts; no expected answer or chosen tool is supplied.
        prompt += "\n\nCurrent project context from the registered fixture:\n" + config.read_text()
        prompt += "\nSelected editor source src/Example.cs:\n" + source.read_text()
        for name in ("impact", "mcp-routing"):
            prompt += f"\nAvailable skill reference .agents/skills/axsk/references/{name}.md:\n" + (ROOT / f"skills/axsk/references/{name}.md").read_text(encoding="utf-8")
        import anyio
        schemas = anyio.run(discovered_schemas, mcp_args, env, root / "discovery.log")
        prompt += "\nTool metadata discovered from this fixture's actual authenticated MCP stdio server:\n" + json.dumps(schemas)
        command = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--sandbox", "read-only", "--skip-git-repo-check", "--json",
                   "-C", str(repo), "-c", 'mcp_servers.axiom.command=' + json.dumps(shutil.which("python")),
                   "-c", 'mcp_servers.axiom.args=' + json.dumps(mcp_args),
                   "-c", 'mcp_servers.axiom.env.AXIOM_HOME=' + json.dumps(str(home)), prompt]
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=180)
        after = hashlib.sha256(source.read_bytes()).hexdigest()
        # Retain task-local events; replace local fixture and workspace paths.
        text = result.stdout.replace(str(root), "<fixture>").replace(str(ROOT), "<skills-repo>")
        text = text.replace(str(args.mcp_root.resolve()), "<mcp-repo>")
        events = []
        for line in text.splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: continue
        report = {"prompt": prompt, "codex_version": subprocess.check_output(["codex", "--version"], text=True).strip(),
                  "engine_sha256": hashlib.sha256(args.daemon.resolve().read_bytes()).hexdigest(),
                  "exit_code": result.returncode, "source_preserved": before == after, "source_sha256": before,
                  "scope": "native-windows-isolated-project-with-real-read-scoped-mcp", "events": events,
                  "stderr": result.stderr.replace(str(root), "<fixture>").replace(str(ROOT), "<skills-repo>"),
                  "plugin_namespace": "not_run", "desktop_ui": "not_run"}
        if result.returncode: report["status"] = "failed"
        else: report["status"] = "recorded-awaiting-independent-trace-review"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("Native host evaluation exit", result.returncode, "source preserved", before == after)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--daemon", type=Path, required=True); p.add_argument("--mcp-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    verify(p.parse_args())
