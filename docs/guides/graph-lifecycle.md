# Build, keep current and query your code graph

Skills teach the assistant which tools to use and how to verify their results. `axiom-graphd` analyzes source and publishes graph generations. Its daemon detects saved file changes and refreshes that graph. `axiom-mcp` lets the assistant query the published data with scoped credentials and bounded responses.

Installing skills alone does not build a graph, start a watcher or connect MCP.

| Your request | Skill | Tool and prerequisites | Evidence of success |
|---|---|---|---|
| Build the first graph | `graph-build` | Installed `axiom-graphd`, supported analyzer, selected solution and repository bindings | Published generation, source coverage and a known-symbol query |
| Refresh the graph when source changes | `graph-watch` | Existing graph, registered solution, running graph daemon and its file watcher | A later generation contains the saved change without manual reconciliation |
| Find code, callers or dependencies | `graph-context` | Configured Axiom MCP connection, scoped read credential and published graph | Bounded `graph_query` result with source locations and generation provenance |
| Assess a change | `graph-impact` | Same MCP read connection and selected target | Observed dependencies compared with expectations, including coverage limits |
| Establish a refresh barrier after edits | `graph-reconcile` | MCP control connection and reconcile authority | Completed bounded job and verified scope; not an extra per-save watcher |

## 1. Build with the engine

Ask the assistant to use `graph-build` for the selected repository and solution. It checks the engine and language support, reviews registration if needed, then performs the initial full reconciliation. Registration and graph writes stay within that requested scope.

```text
$axiom:graph-build Build the first graph for this solution and verify a known symbol.
```

The skill uses actual `axiom-graphd solution register`, `reconcile` and `status` commands. A bounded CLI query can serve as a setup smoke check before MCP is configured. Normal assistant questions use MCP once it is connected. An empty graph or an unsupported language is not successful indexing.

See the [engine command reference](https://github.com/orchex006/axiom-graphd/blob/main/docs/reference/axiom-graphd.md) for operator commands.

## 2. Keep the graph current with the daemon

Ask for `graph-watch` after the first graph is published:

```text
$axiom:graph-watch Keep this graph current when I save source files and verify one refresh.
```

The skill checks for an existing service and reuses it. An authorized foreground session runs `axiom-graphd serve`; the daemon owns detection, dirty-scope reconciliation and publication. `serve` covers registrations in its instance, so inspect that scope before starting it. There is no per-solution `serve --solution` flag.

The current engine polls files. A save should produce a later graph generation containing the change. Verify that within a deadline without manually reconciling between the save and observation. Pending work, ignored paths and unsupported files remain explicit. This automatic graph refresh does not restart or hot reload the application being analyzed.

## 3. Connect MCP and ask questions

Configure the [MCP gateway](https://github.com/orchex006/axiom-mcp#run) in your assistant with private credential references and read access to the selected solution/projects. Keep `AXIOM_HOME`, instance selection and repository bindings consistent with the engine. Skills installation does not provision that connection or its credentials.

```text
$axiom:graph-context Find OrderService and explain its dependencies through Axiom MCP.
$axiom:graph-impact Check which callers may be affected by changing this method.
```

The assistant discovers the host's Axiom MCP tools, checks `graph_status`, searches with `graph_query`, then queries a selected node. Tool prefixes depend on the host; use its discovered tool names. These are MCP argument examples, not shell commands:

```json
{"solution_id":"my-solution","operation":"search","query":"OrderService","consistency":"allow_stale","max_nodes":20,"max_bytes":8192}
```

After selecting an unambiguous node from that response:

```json
{"solution_id":"my-solution","operation":"context","target":"<node-id-from-search>","projection":["identity","relations","source_locations","coverage"],"depth":1,"max_nodes":20,"max_edges":40,"max_bytes":8192,"consistency":"allow_stale"}
```

`search` accepts text in `query`; traversal operations use `target`. An explicit traversal projection must include `source_locations`. Use each discovered operation's schema rather than passing the same arguments to every query. Read only the source locations needed to verify the answer; do not load graph shards into model context.

Valid published snapshots can support MCP reads while the daemon is offline. Automatic refresh still requires the daemon. Report the returned generation, freshness, coverage and truncation: `allow_stale` is suitable for observing watcher publication, but it does not prove the graph matches current source. `require_fresh` can enqueue reconciliation and requires reconcile authority; it is not an automatic upgrade of a read-only caller's permissions.

## When a step is unavailable

| Missing dependency | Next step |
|---|---|
| Engine executable | Follow the [runtime installation guide](https://github.com/orchex006/axiom-cli/blob/main/docs/INSTALL.md) |
| Analyzer support | Report the unsupported language or partial coverage |
| Registration or first generation | Use `graph-build` for the authorized project |
| Automatic refresh | Check daemon ownership, watcher mode and changed-file scope with `graph-watch` / `graph-doctor` |
| MCP tools or authorized access | Configure the gateway and scoped credential references; discovery alone is not authenticated access |
| Graph unavailable during a question | Report graph evidence as unverified and use permitted source inspection without silently installing, rebuilding or starting services |

Host completion hooks are optional coordination. They do not implement the engine's file watcher or establish MCP readiness. See the [agent workflow reference](agent-workflow.md) for budgets, cancellation and completion behavior.
