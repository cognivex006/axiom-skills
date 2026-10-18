# Discovered MCP routing

Discover actual tool names, descriptions and operation schemas before constructing
arguments. Do not hard-code host prefixes. Confirm authenticated read scope using
status/version, search the named symbol, resolve returned candidate identities, then
request bounded relations and relevant source locations. Read only returned source
ranges. Preserve direction, resolution, generation vector, verification and limits.

Known capabilities include graph_status, graph_version, graph_query, graph_reconcile,
graph_job and graph_verify; discovery is not authorization. A read-only token cannot
inspect every job or invoke verify/reconcile. Use `consistency=allow_stale` while
observing watch publication. `require_fresh` can enqueue work and must not hide a
watcher failure or grant write authority to a read-only question.

Search uses the discovered query/bounds; traversal uses an observed node ID as target
and an explicit source_locations projection. Do not invent a symbol argument, add
traversal fields to search, select the first duplicate candidate, or concatenate
graph shards into context. Multiple overloads/projects require contextual resolution
or a concise choice. Missing/auth-denied/stale/partial MCP is degraded or unverified;
permitted source inspection can continue without claiming graph verification.

For an authorized local gateway start, first inspect the installed command help.
Current Axiom supports `axm mcp start` with an automatically reserved loopback
port; use its reported endpoint rather than assuming port 8765. Repeating the
same launch reuses only a matching owned instance. Explicit ports and Host/Origin
policies remain explicit; do not broaden them or stop a foreign listener to make
startup succeed. Use `axm mcp status`, `axm mcp list` and `axm mcp stop` for the
owned lifecycle. Multiple instances require an explicit selection.

`axm doctor` describes installation health and reports MCP graph readiness
separately. `axm mcp doctor` checks component compatibility, credentials and graph
query/control readiness; `--verbose` retains technical diagnostics. A listening
gateway or successful `/healthz` alone does not establish graph access. Diagnosis
does not authorize starting the gateway, modifying credentials or writing config.
