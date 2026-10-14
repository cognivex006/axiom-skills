# Axiom Skills

Unreleased workflow preview on the feature branch. Published 0.1.7 remains unchanged;
this work does not publish or prepare a 0.1.8 release.

Tell your assistant what graph work you need. Default discovery has two entrypoints:
`axge` for graph workflows and `axm` for ecosystem installation/update.

```text
$axge build
$axge watch
$axge ask the relation from method PingPong on this project
$axge impact remove method RemoveFilesAsync
$axge export this graph
$axge doctor
$axge doctor upgrade
$axge version
$axm install
$axm update
```

Text after a skill is an intent, not a shell command. Impact removal is analysis-only.
Codex plugins may use `$axiom:axge`; other hosts retain their own namespace. Only
actual host discovery confirms invocation syntax. Graph reads use discovered,
authenticated MCP tools and bounded source evidence.

Follow [getting started](docs/GETTING-STARTED.md) for runtime, plugin and MCP setup,
[host installation](marketplace-plugins/README.md) for package entrypoints, and
[graph lifecycle](docs/guides/graph-lifecycle.md) for selected workflows and limits.
Installed users do not need private specs or contributor task cards.

The engine creates/refreshes the graph; the watcher owns source changes. Builds are
incremental unless a full rebuild is explicitly requested. Read-only questions and
exports do not start services, install software or reconcile implicitly. Ask/impact
reports retain generation, freshness, coverage and unresolved/truncated limits.
Exports retain selected scope and verified snapshot provenance.

This branch adds build/watch/export facades and measured engine cycles. Inspect
installed help before using them: older 0.1.7 engines use reconcile/serve/render and
may lack JSON export or cycle telemetry. An installed plugin is separate from a
working graph/MCP connection. Unrun host behavior is unverified.

Legacy graph-* entrypoints are available only in an explicit compatibility package
until 0.2.0; see [migration](docs/WORKFLOW-MIGRATION.md). Existing released packages
are immutable. Default packages contain two skills, including their references.

For contributors, read [Development.md](Development.md) and [Changelog.md](Changelog.md).
