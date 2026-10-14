# Axiom plugin

Eight skills for understanding code, checking change impact and operating the Axiom graph ecosystem.

Register this package with your assistant, then install the `axiom` plugin from the `axiom-skills` marketplace. In Codex CLI:

```sh
codex plugin marketplace add /absolute/path/to/the/package-root
codex plugin add axiom@axiom-skills
codex plugin list --marketplace axiom-skills
```

The package root contains `.agents/plugins/marketplace.json` and this `plugins/axiom` directory. Open a new session after installation; restart the desktop app if new skills do not appear.

Choose `axge` to find relevant code, `axge impact` before editing, or `axge doctor` to diagnose an unavailable graph. Graph operations need the Axiom runtime and a configured MCP connection. This plugin does not start a server or change host permissions.

[Installation guide](https://github.com/orchex006/axiom-skills/blob/main/marketplace-plugins/README.md) · [Getting started](https://github.com/orchex006/axiom-skills/blob/main/docs/GETTING-STARTED.md)
