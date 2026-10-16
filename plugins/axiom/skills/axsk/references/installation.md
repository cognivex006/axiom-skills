# Installation and repair

Resolve OS/architecture and existing installation. Inspect `axm --help`/version and
owner-published artifact metadata. Use the recorded release/version/hash/platform;
never fabricate a target, URL, executable or release. A missing executable is a
prerequisite, not a successful install. Skills and host plugin registration are
separate from graph runtime/MCP setup.

The distribution owner's verified bootstrap assets are install.ps1 and install.sh
under the axiom-cli GitHub Release. Select an exact reviewed release asset before
execution; the bootstrap verifies the archive digest and delegates to `axm install`.
Installed `axm install --dry-run` can produce a reviewable automation plan; use the
documented exact approved digest only when actually authorized. Human consent or an
explicit request for unattended installation governs confirming/noninteractive forms.
Do not silently alter PATH, elevate privileges or install global software.

Use platform-appropriate native support. Do not require WSL, Docker, Bash, Node or a
compiler to consume a native Windows artifact. Treat actual missing mandatory
runtime dependencies and unsupported platforms as refusals before mutation. Keep
Windows/native Linux/macOS/WSL execution evidence distinct.

Preserve source, user data, old owned generations and human files. Modified/unowned
legacy installations require an explicit adoption/repair plan; never delete them.
Apply only the reviewed target/state, verify installed `axm version` and `axm doctor`,
and retain existing rollback semantics. Report failed/NotReady/not_run legs honestly.

For managed Codex onboarding use supported `axm install --host codex` or `axm skills install codex`; inspect the plan and preserve existing marketplaces. After registration open a new session and verify the discovered skill. `axm skills doctor codex` reports registration separately from MCP query readiness. Other hosts require their documented adapters.
