# Export the selected graph

Use the current conversation's selected solution/projects, node IDs, filters and
generation context. Without a selection, resolve the current registered project.
Ask only if ambiguity remains. Never widen a discussed subgraph to the whole solution.
Read runtime-capabilities.md and graph-quality.md.

Default to a versioned JSON artifact from `axge export` when the installed parser
supports it. Pass explicit selected project/node arguments and a new output directory.
HTML is an additional renderer format. Selection uses published node IDs, not guessed
names. Export pins one catalog vector and verifies exact manifest/shard checksums;
missing/corrupt members fail. It does not rebuild or refresh implicitly.

Report artifact path, format, size/hash, scope, catalog/generation vector, completeness,
coverage, source_fidelity and limits. Full selected projects and filtered projections
are distinct. Do not dump all graph JSON into model context; let the serializer write
the file. Never include credentials, local bindings, sensitive absolute paths, DB/WAL,
locks or logs, alter source/Git index, commit, or publish externally automatically.

Advanced checkpoint/source-selector requests must identify staged/worktree/commit
source and inspect actual supported capabilities. Current engine live/checkpoint lane
publication is not proof that the checkpoint matches staged source. A worktree/live
export says published_source_not_staged_verified. Commit-bound fidelity requires a
verified staged-source snapshot with the same staged source; never modify the user's
index or manually edit generated JSON to make the claim true. If that operator is
unavailable, report the unsupported source-selector capability rather than inventing
an export flag or redirecting checkpoint into doctor.

For a selected MCP projection, pass its observed node IDs and edge IDs with --exact-projection and its project_generations as repeated --project-generation ID=SHA256. An empty selected edge list remains empty; a retained snapshot is read exactly. Never silently switch a conversation snapshot to a newer catalog. If filters or retained generations cannot be represented/loaded, report that limitation instead of widening the export.

Do not confuse the MCP catalog_generation_id vector digest with the engine catalog manifest hash. Use observed project_generations for --project-generation; only an actual engine catalog identity may be passed to --catalog-generation. A missing retained vector is a snapshot-unavailable prerequisite, not permission to export latest.
