# Runtime capabilities

Check installed `axge --help`, `axge version --json` and discovered MCP schemas.
The unreleased workflow facade supports build/watch/export. Released 0.1.7 engines
may only expose reconcile/serve/render; do not infer these new verbs from skill names.

| Skill intent | Facade when supported | Earlier capability |
|---|---|---|
| build | `axge build --solution ID [--project ID] [--full] --json` | reviewed `reconcile --scope dirty` (initial inventory) or explicit `--scope full` |
| watch | `axge watch --json` | `axge serve --json`, instance-wide polling |
| export | `axge export --solution ID [--project ID]... [--node-id ID]... --out NEW-DIR [--format json|html] --json` | render for HTML; JSON export unsupported unless an authoritative serializer is available |
| ask/impact | discovered MCP structured tools | No natural-language engine verb |
| doctor/version | actual engine diagnostic/version commands | read-only |

No per-project watch isolation, LLM parser, implicit full rebuild or guessed terminal
ask/impact command is advertised. When another daemon owns the writer, reuse its
authorized control interface or diagnose the refusal; never clear locks or start
another writer. A CLI build success does not establish MCP access.

Engine work_cycle events arrive on stderr with a typed cycle object. Normal `--json`
stdout remains one object; these events are not MCP protocol output. Earlier engines
without cycle telemetry report processing duration as unavailable with a reason.

For a selected MCP projection, pass its observed node IDs and edge IDs with --exact-projection and its project_generations as repeated --project-generation ID=SHA256. An empty selected edge list remains empty; a retained snapshot is read exactly. Never silently switch a conversation snapshot to a newer catalog. If filters or retained generations cannot be represented/loaded, report that limitation instead of widening the export.

Do not confuse the MCP catalog_generation_id vector digest with the engine catalog manifest hash. Use observed project_generations for --project-generation; only an actual engine catalog identity may be passed to --catalog-generation. A missing retained vector is a snapshot-unavailable prerequisite, not permission to export latest.
