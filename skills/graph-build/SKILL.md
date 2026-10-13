---
name: graph-build
description: Create the first Axiom code graph for a selected solution using the installed graph engine, then verify published generations, source coverage and a bounded query. Use for initial indexing or an explicitly requested full rebuild, not routine edits.
---

# Build a code graph

The skill coordinates `axiom-graphd`; the engine performs inventory, parsing, dependency analysis and graph publication. It cannot build a graph without the installed engine and a supported analyzer.

## Resolve the target

Read repository instructions and `.axiom/agent/POLICY.md` if present. Resolve the repository roots, selected solution/project IDs, existing registration, supported source languages and the intended `AXIOM_HOME`. Keep the same instance home across daemon, operator commands and MCP. Ask for missing scope; do not infer permission to index unrelated repositories.

Use `axiom-graphd version --json`, `axiom-graphd solution list --json` and `axiom-graphd status --solution <solution-id> --json`. A missing executable is a prerequisite failure, not a successful graph build. Offer the installation guide; do not silently install software.

## Register when needed

For an unregistered solution, prepare a `solution.json` and `bindings.json` for the reviewed scope. A minimal single-project declaration is:

```json
{"id":"my-solution","profile":"default","catalog_host_repo":"main-repo","projects":[{"id":"app","repo_id":"main-repo","path":"src"}]}
```

The corresponding binding uses the actual absolute repository root:

```json
{"bindings":{"main-repo":"<absolute-repository-root>"}}
```

Review the dry-run before applying registration:

```text
axiom-graphd solution register --config <solution.json> --bindings <bindings.json> --dry-run --json
axiom-graphd solution register --config <solution.json> --bindings <bindings.json> --apply --json
```

Apply only within the user's authorized setup scope. Preserve existing registration and human files. Do not alter source files, project manifests or ignore rules to make indexing appear successful.

## Build and verify

The initial build, or an explicitly requested full rebuild, uses:

```text
axiom-graphd reconcile --solution <solution-id> --scope full --json
axiom-graphd status --solution <solution-id> --json
axiom-graphd query context --solution <solution-id> --symbol <known-symbol> --max-nodes 20 --max-bytes 8192 --json
```

Check the actual reconcile result, published generation and coverage, then query a symbol known to exist in the selected source. Do not treat exit zero, an empty graph, unsupported-language coverage or process liveness as complete indexing. A query can be ambiguous; narrow it rather than inventing a node identity.

If another daemon owns the instance, use the configured control/MCP reconcile interface and bounded job polling. Do not start a second writer or clear its lock. A first full build is deliberate work; routine edits should use dirty-scope reconciliation or `graph-watch`.

Report solution/projects, instance home, engine/analyzer versions, observed generation, source coverage, query evidence and unresolved limitations. Do not load graph shards into model context or edit the generated graph directly.
