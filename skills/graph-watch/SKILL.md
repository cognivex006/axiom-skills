---
name: graph-watch
description: Keep an existing Axiom code graph updated as source files change by running the graph engine's watcher/reconcile loop, and verify automatic publication after a save. Use for continuous graph refresh, not hot reloading application binaries or models.
---

# Update the graph on source changes

The engine watches or polls source files, marks changed scope, reconciles and publishes new graph generations. This skill coordinates that lifecycle; it does not implement a watcher or parse source itself.

## Preconditions

Resolve the existing solution/project registration and the same `AXIOM_HOME` used by the graph runtime. Verify `axiom-graphd version --json` and the current `axiom-graphd status --solution <solution-id> --json`. Use `graph-build` if the initial graph is missing. Preserve project files, bindings and credentials.

Inspect `axiom service status --json` before starting another daemon. Reuse the managed service if it is already running. Starting or changing persistent service configuration must stay within the user's authorized scope; do not install a service merely to answer a read-only question.

## Start continuous refresh

For an authorized foreground session, run the actual installed command as program plus argv:

```text
axiom-graphd serve
```

Keep its process handle and diagnostics. A foreground loop is long-lived; use an asynchronous process session rather than waiting indefinitely for it to exit. Do not fabricate `axiom-graphd watch` or run a second writer while the instance lock is held. Use the supported supervisor for an explicitly requested persistent service.

`serve` watches the registrations in the selected instance; it has no per-solution `--solution` switch. Inspect that instance's registrations before starting it. If they include repositories outside the authorized scope, resolve that scope or use an approved dedicated instance. Keep its `AXIOM_HOME` and bindings aligned with MCP. The MCP process serves the assistant's requests; file watching belongs to `axiom-graphd`, not MCP or the skill.

The current engine uses polling to detect changes and then reconciles changed scope. Report the observed watcher mode honestly; polling is automatic refresh, not proof of a native filesystem-event backend. Native events, polling and a one-time inventory are different states.

## Verify refresh after a save

Record the current published generation and a bounded query result for a known source symbol. Observe a user-authorized source edit/save, or use a separate temporary test project when demonstrating the workflow. Do not insert demonstration code into a user's project without permission.

Within a bounded deadline, inspect:

```text
axiom-graphd status --solution <solution-id> --json
axiom-graphd query context --solution <solution-id> --symbol <changed-symbol> --max-nodes 20 --max-bytes 8192 --json
```

Confirm that a later generation reflects the changed source. Do not call manual `reconcile` between the save and this verification: that would demonstrate manual refresh rather than the watcher. Inspect queue/freshness/coverage if a save is not reflected; surface unsupported files, ignored paths, read-only mounts or watcher degradation instead of claiming success.

These CLI queries are setup diagnostics when MCP is not connected. With MCP connected, use its discovered `graph_status` and bounded `graph_query` tools to verify the changed symbol in a later generation. Use `consistency=allow_stale` for this observation and inspect the returned generation; `require_fresh` may enqueue reconciliation and would obscure whether the watcher alone refreshed the graph. Follow `graph-context` for code questions and `graph-impact` for dependency reviews.

The daemon batches changes. Do not full-rebuild on every keystroke or tool call. A pending job or timeout remains pending, not fresh. Graph refresh does not hot reload the application being analyzed.

If the watcher is already updating the relevant scope, observe that work within the deadline before requesting another refresh. Use `graph-reconcile` for an explicitly requested dirty-scope barrier at a coherent change boundary, not as an additional watcher on every save.

Stop only a foreground process started by this skill, using cooperative termination and a bounded wait. Keep shared services running unless stopping them was authorized. Never delete a lock, live database, graph generations or source files as a watcher workaround.

Report the solution, process/service ownership, watcher mode, before/after generations, changed-source query evidence, refresh delay and any unresolved limitations.
