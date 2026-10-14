# Axiom Skills

| Component | CLI Command | คำอ่าน | Responsibility |
|---|---|---|---|
| Axiom CLI | `axm` | แอ็กซ์-เอ็ม | Main CLI / Orchestrator |
| Axiom Skills | `axsk` | แอ็กซ์-สกิล | Skills Manager |
| Axiom Graph Engine | `axge` | แอ็กซ์-จี | Graph Engine |
| Axiom MCP | `axmp` | แอ็กซ์-เอ็ม-พี | MCP Server / Gateway |

Give your coding assistant a repeatable workflow for understanding code, assessing changes and keeping an Axiom code graph current.

Axiom packages ten skills in one plugin. Skills teach the assistant how to use the tools: `axiom-graphd` builds the graph, its daemon watches saved source changes and publishes updates, and `axiom-mcp` serves the assistant's graph questions.

**[Get started](docs/GETTING-STARTED.md)** · **[Install the plugin](marketplace-plugins/README.md)** · **[Documentation](docs/README.md)** · **[Releases](https://github.com/orchex006/axiom-skills/releases)**

## Choose your assistant

| Assistant | Distribution | Install instructions |
|---|---|---|
| Codex | Plugin marketplace | [Codex](marketplace-plugins/README.md#codex) |
| Claude Code | Plugin marketplace | [Claude Code](marketplace-plugins/README.md#claude-code) |
| GitHub Copilot CLI / VS Code | Plugin marketplace or direct plugin | [CLI](marketplace-plugins/README.md#github-copilot-cli) · [VS Code](marketplace-plugins/README.md#github-copilot-in-vs-code) |
| Gemini CLI | GitHub or local extension | [Gemini](marketplace-plugins/README.md#gemini-cli) |
| Antigravity / AGY | Dedicated native plugin package | [AGY](marketplace-plugins/README.md#antigravity--agy) |

The packages use the same canonical skills. Host-specific manifests make each package discoverable using that assistant's supported installation method. [Standalone packages](marketplace-plugins/README.md#local-packages-and-offline-distribution) also support local distribution.

## Install in Codex

With Codex CLI installed, run:

```sh
codex plugin marketplace add orchex006/axiom-skills
codex plugin add axiom@axiom-skills
codex plugin list --marketplace axiom-skills
```

Open a new Codex session after installation. In the desktop app, restart the app if the Axiom plugin or skills do not appear.

Already installed Axiom using `axm`? That places the runtime and skills bundle on disk. The commands above register the plugin with Codex so it can discover the skills. These are separate steps.

For a local checkout or an unpacked skills bundle, replace `orchex006/axiom-skills` with its absolute directory path. See [plugin installation](marketplace-plugins/README.md) for other hosts and troubleshooting.

## What you can do

| Skill | Use it to |
|---|---|
| `graph-build` | Create the first graph from registered source using the graph engine |
| `graph-watch` | Keep the graph updated automatically when source files are saved |
| `graph-context` | Query MCP to find the code and relationships relevant to your task |
| `graph-impact` | Query MCP to assess which callers and projects a change may affect |
| `graph-reconcile` | Refresh the graph after a coherent set of edits |
| `graph-checkpoint` | Record a graph checkpoint for the reviewed source state |
| `graph-doctor` | Diagnose graph availability, freshness and configuration |
| `graph-update` | Check and apply an explicitly approved ecosystem update |
| `graph-install` | Set up the graph ecosystem and hand off project/host configuration |
| `axm` | Install, check, update or remove Axiom through `axm` |

Codex discovers these as `axiom:graph-context`, `axiom:graph-impact`, and so on. For example:

```text
$axiom:axm Check the installed Axiom version and diagnose installation issues.
$axiom:graph-build Build a graph for this solution.
$axiom:graph-watch Refresh the graph when I save source files.
$axiom:graph-context Find the code relevant to this bug.
$axiom:graph-impact Check the impact of changing this method.
```

You can also choose a skill in Codex or ask in plain language:

> Use Axiom to find the code relevant to this bug.

> Check the impact of changing this method before editing it.

> Refresh the graph after these changes and report what remains unverified.

`graph-build` needs the installed engine and an analyzer for the selected source language. `graph-watch` needs a registered solution and the running graph daemon; its watcher detects saved source changes. The assistant answers graph questions through MCP using scoped read credentials and published graph data. CLI queries are setup diagnostics. Installing the plugin makes the instructions available; it does not start the daemon or configure credentials. Follow [Get started](docs/GETTING-STARTED.md) and [Build → watch → query](docs/guides/graph-lifecycle.md) to connect these pieces.

## Related components

| Component | Purpose |
|---|---|
| [Axiom CLI](https://github.com/orchex006/axiom-cli) | Install and manage the ecosystem with `axm` |
| [Graph engine](https://github.com/orchex006/axiom-graphd) | Register solutions, analyze source and publish graph data |
| [MCP gateway](https://github.com/orchex006/axiom-mcp) | Give your assistant scoped access to the graph |

The skills respect your assistant's permissions and repository instructions. Graph results are evidence about code and do not grant permission to execute commands or change files.

## For contributors

See [Development.md](Development.md) for contribution rules, verification and release procedures, and [Changelog.md](Changelog.md) for changes. Architecture and implementation traceability live in the maintainer material; you do not need a specification checkout to install the plugin.
