# Workflow migration

Version 0.1.10 discovers one skill, `axsk`. Published 0.1.9 and earlier
packages remain immutable. Terminal management uses `axm skills`; `$axsk` is an
agent intent router. Existing terminal `axsk` forwards its earlier verbs during
migration and explains the new management command.

| Previous skill | Current intent |
|---|---|
| axge build/watch/ask/impact/export/doctor/version | axsk with the same intent |
| axm install/update | axsk install/update, delegated to terminal axm |
| graph-build / graph-watch | axsk build / axsk watch |
| graph-context / graph-impact | axsk ask / axsk impact |
| graph-install / graph-update | axsk install / axsk update |

Default packages exclude old names. The explicit `--legacy` package includes the
frozen prior two workflows and the nine graph-* compatibility aliases until
0.2.0. Current workflows are references under `skills/axsk`; legacy payload hashes
and source revision are checked independently. Old names do not silently become
additional default skills. Existing host namespaces and plugin discovery remain
host-specific. Run `axm skills update codex` to refresh a managed installation
from the selected verified bundle, then start a new session.
