# Roadmap

**English** | [Türkçe](TODO.tr.md)

## Documentation

- [x] Show English and Turkish options together and mark the active document language.

## Quality Assurance

- [x] Normalize resolved temporary paths in cross-platform environment tests.
- [x] Enforce lowercase Conventional Commit subjects with a 45-character limit.

## Configuration Discovery

- [ ] Search parent directories for the nearest `.venvm.json` file.
- [ ] Stop discovery at the filesystem root or an explicit project boundary.
- [ ] Show the detected project root in diagnostic output.

## Configuration Layers

- [ ] Apply settings in this order, from highest to lowest priority:
  command-line options, `VENVM_*` environment variables, `.venvm.local.json`,
  `.venvm.json`, global user configuration, and built-in defaults.
- [ ] Store global configuration in the platform-specific user config directory:
  - Windows: `%APPDATA%\venvm\config.json`
  - Linux: `${XDG_CONFIG_HOME:-~/.config}/venvm/config.json`
  - macOS: `~/Library/Application Support/venvm/config.json`
- [ ] Add a configuration schema version for future migrations.
- [ ] Write configuration changes atomically to avoid partial files.

## Configuration Commands

- [ ] Add `venvm config path` to print all active configuration paths.
- [ ] Add `venvm config show` to display stored values.
- [ ] Add `venvm config show --effective` to display merged values and their sources.
- [ ] Add `venvm config get KEY`.
- [ ] Add `venvm config set KEY VALUE` with project, local, and global scopes.
- [ ] Add `venvm config unset KEY`.
- [ ] Add `venvm config doctor` to report invalid paths and configuration conflicts.

## Local Overrides

- [ ] Support `.venvm.local.json` for developer-specific settings.
- [ ] Add `.venvm.local.json` to `.gitignore` when created by venvm.
- [ ] Keep shared defaults in `.venvm.json` and machine-specific paths in the local file.

## Project Initialization

- [ ] Add an interactive `venvm init` command.
- [ ] Let `venvm init` select a default environment, script, or module.
- [ ] Let `venvm init` create `.venvm.json` and update `.gitignore` with confirmation.

## Central Project Registry

- [ ] Add `venvm register NAME` to associate a project name with its path.
- [ ] Add `venvm projects` to list registered projects.
- [ ] Add `venvm use NAME` to run venvm for a registered project.
- [ ] Add `venvm unregister NAME`.
- [ ] Store project names and paths only; do not move virtual environments.
- [ ] Detect and report stale project paths.

## Environment Variables

- [ ] Support `VENVM_ENV` for the preferred environment.
- [ ] Support `VENVM_CONFIG` for an explicit configuration file.
- [ ] Support `VENVM_NO_INPUT` for non-interactive execution.

## Safety

- [x] Require `--install-deps` before installing dependency files non-interactively.
- [x] Do not let `--yes` alone install dependencies from a cloned repository.
- [ ] Never store secrets in project or global venvm configuration.
- [ ] Validate configured environment and project paths before execution.
