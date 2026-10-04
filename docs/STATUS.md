# Distribution status

Checked on 2026-10-04. This records repository changes and validation, not a
published release. Execution is tracked in [OSS-131](https://linear.app/acturea/issue/OSS-131).

## Entries

| Entry | Repository state | Installation validation |
| --- | --- | --- |
| docpack, glyphweave, hanzi-sort, reviewloop | Existing stable formulae; reviewloop smoke repaired; docpack restored to CI | New CI run pending |
| ScriptMark | Stable v0.2.0 binary formula for macOS/Linux ARM64/x86_64; Python 3.13 wrapper and grading smoke | Full install/test pending |
| Stepwise | HEAD-only CLI formula, excluding private notes | Source build/test pending |
| Foch | HEAD-only CLI formula, with pinned public grammar/schema submodules | Source build/test pending; existing local binary passed the manifest smoke |
| Teaser | README entry and inactive cask template | Await independent runtime namespace and complete signed release bundle; [P-859](https://linear.app/acturea/issue/P-859) |

## Checks completed

- Ruby syntax checks for all formulae, the download strategy and cask template.
- Homebrew style: all seven formulae and the download strategy passed.
- Local strict audit after explicitly trusting the tap in a temporary configuration.
- `actionlint` for the workflow; ShellCheck for modified upstream generators.
- Homebrew metadata produced a complete 14-job macOS/Linux matrix, with HEAD
  enabled only for Stepwise and Foch. No source installation was started.
- Real local Git fixture: a public pinned submodule was fetched; an unavailable
  private notes submodule was skipped. The empty-submodule mode also skipped notes.
- Foch's existing local binary parsed an isolated mod manifest without game data.
  This validates the smoke input; it does not validate the Homebrew-built binary.
- Repaired reviewloop upstream generator reproduced the tap formula byte-for-byte
  with the published version and checksum. The v0.2.1 binary has not been rebuilt.
- `git diff --check`.

## Upstream changes

Initially prepared locally, then delivered through the PRs below:

- `reviewloop/tools/render_homebrew_formula.sh`: mirror the fixed smoke and style.
- `docpack/.github/workflows/release.yml`: target `Acture/homebrew-ac`.
- `foch/scripts/render_homebrew_formula.sh` and its existing typed test: include
  the declared composite license, notices and manifest smoke in the first stable
  formula. Infer its version from the versioned source archive URL.

The user confirmed that Stepwise/Foch releases are imminent. Stable source
formula templates are prepared in [packaging/homebrew/templates/Formula](../packaging/homebrew/templates/Formula/), and
will be activated only after verifying real tags, URLs and checksums. Foch must
use its release source tarball with public submodules, not a GitHub tag archive.
Its existing sync workflow requires `HOMEBREW_TAP_REPO` and a write token. The
repository variable now targets `Acture/homebrew-ac`. The required
`HOMEBREW_TAP_TOKEN` secret is absent, so automated tap publication remains
blocked until a token with write access to that repository is configured.

The three upstream fixes have been merged through their repositories' pull
requests. Future release tags must include those commits to use the repaired
automation; existing tags and published archives are unchanged.

## Python service distribution scope

On 2026-10-03 the user confirmed that both devtunnel-service and trapi2litellm
should support uvx/uv tool, Homebrew and Debian/Ubuntu apt. The private distribution
contract (`notes/python-service-distribution.md`) records installed
entry points, persistent service paths, Python runtime compatibility, `.deb`
release artifacts and a shared signed apt feed. RPM is a later extension.

On 2026-10-04, devtunnel-service's Python `main` has accepted wheel, sdist and
`.deb` artifacts, including Debian/Ubuntu installation and upgrade validation on
amd64 and arm64. Its [product CI passed](https://github.com/Acture/devtunnel-service/actions/runs/37183978494)
for `a78fc33`. The pinned [v0.1.0 Release](https://github.com/Acture/devtunnel-service/releases/tag/v0.1.0)
is now public with wheel, sdist, `.deb` and `SHA256SUMS`; its
[tag and release CI](https://github.com/Acture/devtunnel-service/actions/runs/37190627951)
also passed.

The signed APT implementation is merged into `master`, tracked in
[OSS-33](https://linear.app/acturea/issue/OSS-33). Its [master source CI passed](https://github.com/Acture/homebrew-ac/actions/runs/37190605977),
checking real Signed-By installation, upgrade, tamper rejection and architecture
filtering on the same distribution/architecture matrix. GitHub Pages, a dedicated
archive signing key and the required Actions configuration are established.
The [APT source guide](apt-source.md) records the reviewed public key and setup.

The [first publication](https://github.com/Acture/homebrew-ac/actions/runs/37190797354)
and [live HTTPS acceptance](https://github.com/Acture/homebrew-ac/actions/runs/37190864275)
passed. Each target installed the product by name from
`https://acture.github.io/homebrew-ac/` using the accepted archive key; the served
key and signed InRelease were also compared with the accepted snapshot and
independently verified. Adding trapi2litellm requires its own accepted release
packages; Homebrew service formulae remain a separate unfinished part of OSS-33.
Official distribution inclusion is deferred.

## Repository layout

On 2026-10-04, documentation assets, examples and this status file moved under
`docs/`. Release templates and the shared download strategy moved under
`packaging/`. Active `Formula/` and `Aliases/` remain at the tap root; a future
active cask will use a top-level `Casks/` directory.

The subsequent channel layout puts the actual formulae, aliases, download strategy
and inactive templates in `packaging/homebrew/`, alongside `packaging/apt/`.
Top-level `Formula` and `Aliases` are relative directory symlinks. Foch and
Stepwise resolve their helper from the actual formula location, so loading through
either the symlink or its target uses the same file. Release automation may
continue writing through `Formula/`, but staging and diff checks must use the
tracked `packaging/homebrew/Formula/` path.

CI validates the directory links and continues auditing and testing the full tap.
Homebrew's Git path classification does not recognize the nested source paths;
its update report and changed-only audit/test-bot selection can omit these changes.
Full-tap checks are required for this layout. A future active `Casks` directory
will use the same approach; no cask is enabled by this move.

Channel-layout checks passed locally: seven formulae load through both the
Homebrew entry and the physical directory, both aliases resolve correctly,
the link integrity check and strict full-tap audit pass, all nine Ruby files
pass Homebrew style, workflow lint passes, and public local links resolve.
A Git fixture also verifies that staging detects updates through the physical
formula path, while a pathspec through the directory symlink does not.
Upstream release workflows must use the tracked path before this layout is
published on the tap's default branch. This does not establish full installation
acceptance; the existing installation matrix still has separate failures.

README links, template references, Formula `require_relative` paths and the
preview generator's output directory were updated. The preview generator's font
annotations and integer canvas dimensions were also corrected for Pillow typing.
Moved assets, examples, templates and the download strategy retain their SHA256
digests; no preview images were regenerated.

Validation passed: local Markdown/HTML links, Ruby syntax, Homebrew style for all
seven active formulae, direct loading through Homebrew's Formulary (including
both HEAD download strategies), Ruff lint and formatting of modified lines, ty,
and `git diff --check`. These checks validate the layout and loading;
full installation remains pending.

The user then clarified the ownership boundary: `docs/` is for public material;
internal reviews and plans belong in private `notes/`. The distribution review
and Python service plan moved there, and `docs/patches/` was removed. The three
upstream fixes were refreshed against their current master branches for PR review.
Foch's HEAD formula and stable template were also updated for its published `src/`
layout, including the relocated grammar submodule and CLI crate.

The notes were committed and pushed to the private vault's `project/homebrew-ac`
branch at `a273f8995c1faad3b466c0f1b3c0c38c0d48eb0a` after its required remote
boundary check passed. The code repository now registers this commit as the
optional `notes/` submodule. Only its configuration and gitlink belong in this
public repository; the private note contents remain in the vault.

The project notes were also merged into the total vault: the `homebrew-ac/` tree
matches the project branch exactly, and the merge workflow passed. The submodule's
trusted submission hook is installed; public installation does not require notes.

The user authorized all three PRs and Foch's complete Rust gates, then authorized
merging after reviewing the latest remote layout. The fixes were committed to
separate branches and pushed normally:

- [reviewloop #1](https://github.com/Acture/reviewloop/pull/1), `e266e3e`: ShellCheck,
  generated Ruby syntax/style and byte-for-byte comparison with the repaired tap
  passed. Follow-up `bfbc72f` requires async-trait 0.1.92 to fix the macro's
  `clippy::double_must_use` failure, and honors the manual crates.io publish-skip
  flag before requiring a token. Rust 1.99.0 formatting, strict all-target
  Clippy and all 186 tests passed locally. All workflows passed actionlint;
  both skip-without-token and fail-without-token publishing branches were
  checked without publishing. Remote macOS/Linux
  [CI passed for `bfbc72f`](https://github.com/Acture/reviewloop/actions/runs/37186873352);
  [OSS-298](https://linear.app/acturea/issue/OSS-298) is complete. Squash-merged
  as `4aeff29`; [master CI](https://github.com/Acture/reviewloop/actions/runs/37188081879)
  also passed. The merged tree matches the reviewed PR tree.
- [docpack #1](https://github.com/Acture/docpack/pull/1): release destination and
  public installation documentation now use the maintained tap. Follow-up
  `deb8990` passed CI and was squash-merged as `bce5609`;
  [master CI](https://github.com/Acture/docpack/actions/runs/37188206891) also
  passed. The merged tree matches the reviewed PR tree.
- [Foch #71](https://github.com/Acture/foch/pull/71), `f5ae33c`: renderer check,
  invalid URL rejection, ShellCheck, Ruff, ty and generated Ruby syntax/style
  passed. Complete repository hooks passed: workspace format, strict
  all-target/all-feature Clippy, workspace test build and full workspace tests.
  Remote CI and CodeQL passed, including the Windows installed-package smoke
  and Rust tests on Linux, macOS and Windows.
  The latest layout commit `08b9d1c` keeps reusable maintenance tools under
  `src/tools/foch-dev`, EU4 catalog tooling under `src/tools/eu4-analysis`, and
  installer smoke in its owning application. Release orchestration remains in
  `scripts/`; the CLI and build submodule paths remain compatible. This master
  was merged normally into the PR branch as `298c0d0`; complete local Rust
  gates, renderer regression and workflow lint passed for the combined tree.
  Its [remote CI](https://github.com/Acture/foch/actions/runs/37188200726) and
  [CodeQL](https://github.com/Acture/foch/actions/runs/37188198302) passed, including
  Windows installed-package smoke. Squash-merged as `95f8554`; its separate
  [master CI](https://github.com/Acture/foch/actions/runs/37188855912) is tracked
  independently of the completed PR checks.

Foch's missing Homebrew write credential and first real release sync are tracked
in [OSS-302](https://linear.app/acturea/issue/OSS-302). The sync target is configured;
the credential is still absent. reviewloop's release environment has its declared
crates.io and Homebrew secret names, and docpack has its declared Homebrew secret
name; credential validity and future publication have not been tested.

All three PRs are merged. Source installation and release publication remain
separate pending validation.

## Pending validation

Long-running source builds and installations are to be started by the user.
The machine's installed `acture/ac` tap is a separate checkout: installing its
full formula names before syncing it will exercise the old files.

For a local review of this working tree, run these fish commands to create an
explicitly named temporary tap pointing at the current repository:

```fish
set checktap acture/ac-review
set checkpath (brew --repository)/Library/Taps/acture/homebrew-ac-review
test ! -e $checkpath; or exit 1
ln -s /Users/acture/repos/homebrew-ac $checkpath; or exit 1
brew trust --tap $checktap; or exit 1
brew install --build-from-source $checktap/scriptmark $checktap/reviewloop $checktap/docpack; or exit 1
brew install --HEAD $checktap/stepwise $checktap/foch; or exit 1
for name in scriptmark reviewloop docpack stepwise foch
	brew test $checktap/$name; or break
end
```

The temporary tap installs actual software and does not publish these changes.
Remove its registration after review with `brew untap acture/ac-review` once its
installed formulae no longer depend on it. Existing glyphweave/hanzi-sort behavior
and the Linux builds remain covered by the pending CI run.

The upstream PRs and the private notes branch were published as
recorded above. No GitHub Release or winget submission was performed. The tap's
installation matrix remains pending verification.
