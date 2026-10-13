# Install the Axiom skills plugin

Choose your assistant below. Every package contains the same eight Axiom skills. Plugin installation makes them discoverable; the [graph runtime](https://github.com/orchex006/axiom-cli) and MCP connection are configured separately.

## Codex

```sh
codex plugin marketplace add orchex006/axiom-skills
codex plugin add axiom@axiom-skills
codex plugin list --marketplace axiom-skills
```

Start a new session. Invoke a skill such as `$axiom:graph-context`. Update the registered repository with `codex plugin marketplace upgrade axiom-skills`; use the client plugin manager to refresh the installed package. Remove it with `codex plugin remove axiom@axiom-skills`.

[Official Codex plugin documentation](https://developers.openai.com/plugins/build/plugins)

## Claude Code

In a Claude Code session:

```text
/plugin marketplace add orchex006/axiom-skills
/plugin install axiom@axiom-skills
/plugin
```

Invoke `/axiom:graph-context`, or select a skill in the plugin manager. The `/plugin` manager provides update, enable/disable and uninstall controls.

[Official Claude plugin documentation](https://code.claude.com/docs/en/plugins)

## GitHub Copilot CLI

```sh
copilot plugin marketplace add orchex006/axiom-skills
copilot plugin install axiom@axiom-skills
copilot plugin list
```

You can also install the plugin directly: `copilot plugin install orchex006/axiom-skills:plugins/axiom`. Use `copilot plugin update axiom@axiom-skills` to update and `copilot plugin uninstall axiom@axiom-skills` to remove it. Copilot cloud and desktop/IDE clients have their own plugin or repository-skill setup; the CLI commands do not configure those clients automatically.

[Official Copilot plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)

## GitHub Copilot in VS Code

In a Copilot session using Agent Host, use the plugin manager commands:

```text
/plugin marketplace add orchex006/axiom-skills
/plugin install axiom@axiom-skills
/plugin list
```

Alternatively, open Agent Customizations → Plugins and install from the marketplace. The slash-command manager and Agent Customizations currently use separate inventories; manage a plugin in the interface where you installed it. VS Code UI execution is not verified in this change.

[Official VS Code agent plugin guide](https://code.visualstudio.com/docs/agent-customization/agent-plugins)

For repository-scoped Copilot/cloud skills, the same canonical skill folders can be placed in `.github/skills/` or `.agents/skills/` using [GitHub’s documented skill discovery](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills). Preserve existing same-name directories and configure graph/MCP access separately.

## Gemini CLI

The repository includes an extension entrypoint, so GitHub installation works from its root:

```sh
gemini extensions install https://github.com/orchex006/axiom-skills
gemini extensions list
```

Restart the Gemini session. Use `gemini extensions update axiom` to refresh the extension and `gemini extensions uninstall axiom` to remove it. A local package is also supported: `gemini extensions install /absolute/path/to/axiom-skills/plugins/axiom`.

[Official Gemini extension reference](https://geminicli.com/docs/extensions/reference/)

## Antigravity / AGY

AGY uses its own plugin manifest. Use the dedicated package:

```sh
git clone https://github.com/orchex006/axiom-skills.git
agy plugin install ./axiom-skills/plugins/axiom-agy
agy plugin list
```

Use `/graph-context` to invoke a skill. To refresh a local package, update the checkout and reinstall through the host's plugin manager. Remove it with `agy plugin uninstall axiom`. Antigravity's documented named marketplace installation currently accepts its official marketplace; Axiom does not claim to be listed there. Use the local package, or import it using the appropriate IDE plugin manager.

[Official Antigravity plugin documentation](https://antigravity.google/docs/plugins?tab=cli)

## Local packages and offline distribution

For Codex, Claude and Copilot, pass the absolute repository directory to their marketplace-add command instead of `orchex006/axiom-skills`. Gemini and AGY accept the package directories above directly.

The build tooling produces a separate standalone ZIP for each host with a source revision, exact file hashes and `SHA256SUMS`. Extract a ZIP into a new directory, then pass that directory to the host's local marketplace-add or install command. This package root contains the marketplace/manifest and skills; it does not require the Axiom source workspace. Choose one marketplace source at a time for the `axiom-skills` name to avoid registration conflicts.

## Compatibility and verification

Codex skill discovery is verified on the installed macOS Intel client. All five package layouts, canonical skill parity and archives are tested. Claude, Gemini, AGY and Copilot native installation remains unrun on this machine because their clients are absent; package verification does not prove native runtime, hook behavior or graph/MCP readiness.

Other assistants that implement Agent Skills can consume the `skills/<name>/SKILL.md` folders according to their documented discovery rules. Axiom advertises a host-specific plugin entrypoint only when that host's format is documented.

See [Get started](../docs/GETTING-STARTED.md) and the [skill directory](../README.md#what-you-can-do).
