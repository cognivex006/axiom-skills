# Workflow migration

The unreleased preview replaces ten default skills with `axge` and `axm`. Existing
published 0.1.7 packages remain immutable. Default discovery actually ships two
SKILL.md entrypoints; detailed workflows are references, not additional skills.

| Old entrypoint | New intent |
|---|---|
| graph-build | axge build |
| graph-watch | axge watch |
| graph-context | axge ask |
| graph-impact | axge impact |
| graph-reconcile | Authorized internal dirty refresh/freshness barrier |
| graph-checkpoint | Advanced export source-selector verification |
| graph-doctor | axge doctor |
| graph-install | axm install |
| graph-update | axm update |

For existing consumers, the reviewed host-package builder supports explicit
`--legacy`; it adds nine deprecated forwarding aliases alongside the two current
entrypoints until 0.2.0. Those aliases load the same canonical workflow references.
It does not rely on an invented host hide-skill feature. Default packages exclude
the aliases. Compatibility bytes have a separate checked manifest.

Contributors can generate an unpublished, commit-bound compatibility package with:

```text
python -m release.build_host_packages --out <new-directory> --source-revision <reviewed-feature-sha> --legacy
```

Never install/update a host plugin or publish a package implicitly. Host-specific
namespaces and discovery are tested separately from byte parity. Version remains
0.1.7 with development/unreleased metadata; no 0.1.8 tag/release is created here.
