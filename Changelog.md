# Changelog

## Unreleased

### New Features

- Route graph build/watch/questions/impact/export/diagnostics through axge with selectively loaded references; keep ecosystem lifecycle under axm.
- Ship two default skills with explicit deprecated compatibility aliases through 0.2.0, selected-snapshot exports and measured engine-cycle guidance.

### Known Limitations

- Workflow facades require a matching engine capability; earlier installed engines may use reconcile/serve/render. Native host execution is reported only when tested. No 0.1.8 release is published.

## 0.1.7

### Bug Fixes

- Teach install and diagnostic workflows to check the engine-linked SQLite driver by actual SQL operations, with version numbers informational. Prebuilt installations no longer ask for a Rust compiler or separate SQLite package.
- Align all host plugin payloads with installation versus gateway checks and the private `bin/graphd-engine/` layout.

- Correct the repository marketplace guide to list ten skills and align the optional Copilot catalog version with the plugin. Check declared marketplace versions before packaging. Published standalone 0.1.6 host packages already include the correct version and ten skills.

### Documentation

- Use the canonical public commands in all current examples; access private engine operations through `axm engine`.


- Teach the four canonical commands: `axm`, `axsk`, `axge` and `axmp`. Align graph build/watch, skills management and MCP setup with the actual runtime entrypoints.


- Rename the CLI workflow skill to `axm`, matching the command used for installation, updates and diagnostics. Codex discovers it as `axiom:axm`; package layouts and onboarding use the same name.

- Connect initial graph builds, automatic source-change refresh and MCP-backed code questions in skills and onboarding. Explain engine/analyzer requirements, instance-wide daemon watching, scoped MCP access, operation-specific query arguments and freshness limits.

## 0.1.6

### New Features

- Add `graph-build` to register a selected project, create its first graph with the installed engine and verify a published generation through a bounded query.
- Add `graph-watch` to run continuous source-change refresh and verify that a save produces a new generation without manual reconciliation. Report polling versus native watcher behavior honestly.
- Publish ten canonical skills as standalone Codex, Claude Code, Gemini CLI, Antigravity and Copilot plugin packages, with matching version and payload hashes.

### Documentation

- Use functional language in installation skill descriptions and put graph creation/refresh before runtime management in onboarding.

Full Changelog: [v0.1.5…v0.1.6](https://github.com/orchex006/axiom-skills/compare/v0.1.5...v0.1.6)

## 0.1.5

### New Features

- Add `axm` installation-management guidance and package the canonical graph workflow skills.
- Provide one portable skills bundle; graph runtime and MCP remain separate prerequisites.

## 0.1.4

- Align installation guidance with the one-line update scripts.

## 0.1.3

- Align installation guidance with the one-line ecosystem installer.

## 0.1.2

- Deliver portable skills and canonical bootstrap policy through checked GitHub release assets.

## 0.1.1

- Provide the portable owner skills bundle for Intel Mac testing.

## 0.1.0

- Introduce graph context, impact, reconciliation, checkpoint, diagnostics and installation workflows.
