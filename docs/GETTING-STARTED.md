# Get started with Axiom Skills

A working setup has three parts: the Axiom runtime, the skills plugin in your assistant, and a project/MCP connection for graph operations.

## 1. Install the runtime

Follow the [Axiom installation guide](https://github.com/orchex006/axiom-cli/blob/main/docs/INSTALL.md) for your platform. After installation:

```sh
axm version
axm doctor
```

These commands check the installed ecosystem. Project registration and AI-host setup are separate. Once the plugin is installed, `$axiom:axsk` guides install, repair, update, doctor, version and uninstall through the same `axm` command. SQLite readiness means the graph engine can open and query its linked driver; no matching version or separate system SQLite install is required. Prebuilt releases need no Rust compiler. Use `axm doctor --verbose` for runtime paths and detailed evidence, and `axmp doctor` for gateway credentials and query/control readiness. The CLI manages its private `bin/graphd-engine/` directory, including migration of owned older layouts.

## 2. Add the skills to Codex

The managed host commands are an unpublished development addition. For a released
0.1.9 installation use its versioned manual plugin guide. With a build containing
the managed adapter:

```powershell
axm skills install codex
axm skills doctor codex
```

The manager registers a retained snapshot of the verified installed skills bundle.
Open a new agent session; restart the desktop app if discovery is stale. The host
may expose `$axiom:axsk`. Registration does not establish a successful MCP query.
Other host setup remains in [plugin installation](../marketplace-plugins/README.md).

## 3. Connect a project and MCP

Start with `$axiom:axsk build` to register the selected solution, build its first graph and verify a known symbol. Then use `$axiom:axsk watch` to keep that graph current after source files are saved. Both workflows need `axiom-graphd`; automatic refresh uses its running daemon and current polling watcher. This refresh updates graph data, not application binaries.

Use the [graph engine command reference](https://github.com/orchex006/axiom-graphd/blob/main/docs/reference/axiom-graphd.md) to register your solution and produce its graph. Configure the [MCP gateway](https://github.com/orchex006/axiom-mcp#run) with credentials scoped to that solution and add its launch configuration to your host.

MCP credentials stay private. Registering a skills plugin does not create credentials, register a solution or start an MCP server.

For code questions, the assistant uses `axge ask` or `axge impact` to discover and call MCP `graph_status` / `graph_query`; CLI graph queries are setup diagnostics. Keep the engine and gateway on the same `AXIOM_HOME`, instance and repository bindings. See [Build → watch → query](guides/graph-lifecycle.md) for prerequisites, actual tool routing, bounded query examples and failure recovery.

## 4. Try a skill

In Codex, invoke the discovered skill by name:

```text
$axiom:axsk build Build the first graph for this solution.
$axiom:axsk watch Update the graph when I save source files.
$axiom:axsk ask Find the code relevant to this bug.
```

Or choose `axge` in the skills picker and ask:

> Find the code and relationships relevant to this bug, then read the source files needed to verify the result.

Use `axge impact` for hypothetical change analysis, `axge build` for an authorized refresh, `axge export` for the selected snapshot, and `axge doctor` for diagnosis. The [workflow directory](../README.md) describes the two entrypoints.

## If the skills do not appear

| Symptom | Check or fix |
|---|---|
| `axm` says skills are installed, but Codex shows none | Run `axm skills install codex` on a build containing the adapter |
| Marketplace exists, but the plugin is not installed | Run `axm skills install codex` |
| An existing session shows no new skills | Start a new session; restart the desktop app if needed |
| `codex plugin` is not recognized | Check `codex --version` and the current [Codex plugin documentation](https://developers.openai.com/plugins/build/plugins) before changing the installation |
| Skills appear, but graph operations fail | Check the registered solution, graph freshness, MCP connection and caller credentials |

Historical direct plugin onboarding was observed on Codex CLI 0.162.1 on macOS Intel. The new managed adapter has separate native contract-fixture coverage; actual new-session skill discovery and authenticated graph access require their own host verification. See [host compatibility](host-compatibility.md).
