# Axiom Skills

Use `$axsk` in your agent to build, watch, query, inspect impact and export Axiom
project graphs. The plugin supplies workflow instructions and focused references.

## Install

Install the runtime using the [Axiom installer](https://github.com/orchex006/axiom-cli#install-and-update).
The managed setup below is an unpublished development addition. Published 0.1.9
keeps its original two skill names and [manual plugin registration](https://github.com/orchex006/axiom-skills/blob/v0.1.9/marketplace-plugins/README.md).

```powershell
axm skills install codex
```

Open a new agent session and confirm the discovered skill. A host may display
`$axiom:axsk` or another native namespace. The initial managed adapter is Codex;
[other host instructions](marketplace-plugins/README.md) remain available.

## Update

```powershell
axm update
axm skills doctor codex
```

Managed host content is refreshed from verified installed runtime content during
installation. To refresh only the host registration, use `axm skills update codex`.
Runtime and plugin registration results are reported separately.

## Use the skill

```text
$axsk build
$axsk watch
$axsk ask Find callers of PingPong across projects A, B and C.
$axsk impact What would removing RemoveFilesAsync affect?
$axsk export this graph
$axsk doctor
$axsk version
```

Text after the skill is an agent intent. The workflow resolves registered
projects, discovers scoped MCP tools and keeps the returned generation vectors.
For questions spanning solutions it makes bounded calls per solution and reports
their individual provenance. Graph coverage and unresolved edges stay explicit;
source is consulted when graph evidence is insufficient or needs verification.

## Verify the connection

`axm doctor` checks the runtime. `axm skills doctor codex` checks host registration.
A new session establishes skill discovery. An authenticated graph query verifies
the project/MCP connection. These checks are reported separately.

See [Get started](docs/GETTING-STARTED.md), [graph lifecycle](docs/guides/graph-lifecycle.md)
and [migration](docs/WORKFLOW-MIGRATION.md). Existing terminal `axsk` is deprecated;
all managed installation and update operations belong to `axm`.

## Components and compatibility

`axm` owns runtime and host lifecycle; `axge` analyzes source and publishes graphs;
`axmp` serves the local graph API/MCP connection. The agent skill is `axsk`.
Default packages contain one skill and its references. Explicit compatibility
packages retain prior `axge`/`axm` and graph-* skills through the documented window.
Published releases and historical payloads remain immutable.

For contributors, see [Development](Development.md) and [Changelog](Changelog.md).
