# Axiom Skills

Give your coding assistant a repeatable workflow for understanding code, assessing changes and keeping an Axiom code graph current.

Axiom packages eight skills in one plugin. The plugin works alongside your existing assistant; the graph engine and MCP connection provide the runtime it uses.

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
| `graph-context` | Find the code and relationships relevant to your task |
| `graph-impact` | Assess which callers and projects a change may affect |
| `graph-reconcile` | Refresh the graph after a coherent set of edits |
| `graph-checkpoint` | Record a graph checkpoint for the reviewed source state |
| `graph-doctor` | Diagnose graph availability, freshness and configuration |
| `graph-update` | Check and apply an explicitly approved ecosystem update |
| `graph-install` | Set up the graph ecosystem and hand off project/host configuration |
| `axiom-cli-install` | Install, check, update or remove Axiom through `axm` |

Codex discovers these as `axiom:graph-context`, `axiom:graph-impact`, and so on. For example:

```text
$axiom:graph-context Find the code relevant to this bug.
$axiom:graph-impact Check the impact of changing this method.
```

You can also choose a skill in Codex or ask in plain language:

> Use Axiom to find the code relevant to this bug.

> Check the impact of changing this method before editing it.

> Refresh the graph after these changes and report what remains unverified.

Graph operations need a registered solution, published graph data and a configured MCP connection. Installing the plugin makes the skills available; it does not start the graph daemon or configure credentials. Follow [Get started](docs/GETTING-STARTED.md) to connect these pieces.

## Related components

| Component | Purpose |
|---|---|
| [Axiom CLI](https://github.com/orchex006/axiom-cli) | Install and manage the ecosystem with `axm` |
| [Graph engine](https://github.com/orchex006/axiom-graphd) | Register solutions, analyze source and publish graph data |
| [MCP gateway](https://github.com/orchex006/axiom-mcp) | Give your assistant scoped access to the graph |

The skills respect your assistant's permissions and repository instructions. Graph results are evidence about code and do not grant permission to execute commands or change files.

## For contributors

See [Development.md](Development.md) for contribution rules, verification and release procedures, and [Changelog.md](Changelog.md) for changes. Architecture and implementation traceability live in the maintainer material; you do not need a specification checkout to install the plugin.
