# Installed version facts

Read the installed `axge version --json` and, when available, `axm version --json`,
MCP graph_version and bundle metadata. Report engine/CLI/MCP/skills versions and
schema/analyzer compatibility only when observed. Keep installation, host discovery,
authenticated access and a successful graph query separate.

Bare version is offline. No network update check is required; unavailable components
are unknown, offline or not_checked. Never translate not_checked into up-to-date.
Version does not install, migrate, start/restart a service or change credentials.
