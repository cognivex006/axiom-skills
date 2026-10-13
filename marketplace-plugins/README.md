# Install the Axiom plugin

The Axiom plugin contains eight graph and installation skills. Register it with your assistant to make the skills visible. The [Axiom runtime](https://github.com/orchex006/axiom-cli) and MCP connection are configured separately.

## Codex

```sh
codex plugin marketplace add orchex006/axiom-skills
codex plugin add axiom@axiom-skills
codex plugin list --marketplace axiom-skills
```

For a local checkout or a complete unpacked skills bundle:

```sh
codex plugin marketplace add /absolute/path/to/axiom-skills
codex plugin add axiom@axiom-skills
codex plugin list --marketplace axiom-skills
```

Pass the package root containing `.agents/plugins/marketplace.json` and `plugins/axiom/`. On Windows, use the equivalent absolute Windows path. Registering the marketplace makes the plugin available; `plugin add` installs it.

Start a new session after installation. In the desktop app, restart the app if the plugin list does not refresh. See [OpenAI's plugin documentation](https://developers.openai.com/plugins/build/plugins) for current client behavior.

## Other assistants

Use a local checkout or unpacked skills bundle for these package entrypoints:

| Host | Commands |
|---|---|
| Claude Code | `claude plugin marketplace add <package-root>` then `claude plugin install axiom@axiom-skills` |
| Gemini CLI | `gemini extensions install <package-root>/plugins/axiom` |
| Antigravity CLI | `agy plugin install <package-root>/plugins/axiom` |

Check the installed host's command help and [host compatibility guide](../docs/host-compatibility.md). The commands above describe each package entrypoint; native registration in this change is verified for Codex CLI on macOS Intel, and does not establish other hosts' runtime or hook support.

## Use the skills

Choose a skill or ask your assistant to use Axiom to find relevant code, assess a change's impact or diagnose the graph. See [Get started](../docs/GETTING-STARTED.md) and the [skill directory](../README.md#what-you-can-do).

If the skills appear but graph calls fail, check the registered solution and MCP configuration. The plugin does not install binaries, start servers or configure credentials.
