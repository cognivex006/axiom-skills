# Ecosystem upgrade

Inspect actual installed `axm --help`, version/doctor and recorded channel/metadata.
Use only the update syntax the installed parser supports. `axsk doctor upgrade`
diagnoses graph/schema/MCP compatibility and delegates here; it does not create an
updater or equate source refresh with software/schema upgrade.

Prepare the exact update plan with selected versions, hashes, target, installed
state and mutation scope. Existing consent persists for that exact action; obtain
missing approval at apply. Never forge/copy approval digests, widen scope or silently
replan and apply after drift. Stale plans must be refused and reviewed anew.

The existing distribution/installation engine verifies inputs, drains owned work,
activates atomically, checks health and retains rollback bytes. Skill instructions
do not replace any of those checks. Schema migration, service restart or trust-root
changes require their own actual authorization. Offline/not_checked is not current.

When no canonical entrypoint exists, offer the owner-published update.ps1/update.sh
handoff from an exact reviewed release, preserve old data and diagnose leftover
environment overrides. After apply record actual versions, health, rollback/state
and unsupported/unverified features. An approved plan alone is not an applied upgrade.

For an Axiom-managed Codex plugin use `axm skills update codex` to refresh the verified installed content. A failed/interrupted host change retains recovery data; inspect `axm skills recover codex` and its exact plan before retrying. A runtime success with failed host setup is partial, not a complete agent setup.
