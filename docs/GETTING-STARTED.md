# Get started with Axiom Skills

A working setup has three parts: the Axiom runtime, the skills plugin in your assistant, and a project/MCP connection for graph operations.

## 1. Install the runtime

Follow the [Axiom installation guide](https://github.com/orchex006/axiom-cli/blob/main/docs/INSTALL.md) for your platform. After installation:

```sh
axm version
axm doctor
```

These commands check the installed ecosystem. Project registration and AI-host setup are separate.

## 2. Add the skills to Codex

```sh
codex plugin marketplace add orchex006/axiom-skills
codex plugin add axiom@axiom-skills
codex plugin list --marketplace axiom-skills
```

For a local checkout or the complete unpacked skills bundle, pass that directory to `codex plugin marketplace add` instead of the GitHub repository. The directory must contain `.agents/plugins/marketplace.json` and `plugins/axiom/`.

Start a new Codex session. If the desktop app still shows the old plugin list, restart it. A plugin being listed confirms installation; it does not prove that a graph query or a host completion hook works.

For Claude Code, GitHub Copilot CLI, Gemini CLI or Antigravity, use [the plugin installation guide](../marketplace-plugins/README.md).

## 3. Connect a project and MCP

Use the [graph engine command reference](https://github.com/orchex006/axiom-graphd/blob/main/docs/reference/axiom-graphd.md) to register your solution and produce its graph. Configure the [MCP gateway](https://github.com/orchex006/axiom-mcp#run) with credentials scoped to that solution and add its launch configuration to your host.

MCP credentials stay private. Registering a skills plugin does not create credentials, register a solution or start an MCP server.

## 4. Try a skill

In Codex, invoke the discovered skill by name:

```text
$axiom:graph-context Find the code relevant to this bug.
```

Or choose `graph-context` in the skills picker and ask:

> Find the code and relationships relevant to this bug, then read the source files needed to verify the result.

Use `graph-impact` before a change, `graph-reconcile` after a set of edits, and `graph-doctor` when the graph is missing or stale. The [skill directory](../README.md#what-you-can-do) describes all eight workflows.

## If the skills do not appear

| Symptom | Check or fix |
|---|---|
| `axm` says skills are installed, but Codex shows none | Register the marketplace and install `axiom@axiom-skills` using step 2 |
| Marketplace exists, but the plugin is not installed | Run `codex plugin add axiom@axiom-skills` |
| An existing session shows no new skills | Start a new session; restart the desktop app if needed |
| `codex plugin` is not recognized | Check `codex --version` and the current [Codex plugin documentation](https://developers.openai.com/plugins/build/plugins) before changing the installation |
| Skills appear, but graph operations fail | Check the registered solution, graph freshness, MCP connection and caller credentials |

Onboarding commands are checked with Codex CLI 0.162.1 on macOS Intel. Plugin discovery, graph/MCP queries and host hooks are separate checks; see [host compatibility](host-compatibility.md) for advanced adapter details.
