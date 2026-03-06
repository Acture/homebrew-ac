# Acture Homebrew Tap

[![CI](https://github.com/Acture/homebrew-ac/actions/workflows/brew-ci.yml/badge.svg?branch=master)](https://github.com/Acture/homebrew-ac/actions/workflows/brew-ci.yml)
[![License](https://img.shields.io/github/license/Acture/homebrew-ac)](LICENSE)
![Platforms](https://img.shields.io/badge/platform-macOS%20%2B%20Linux-C67A3C)

Author-maintained Homebrew tap for small Rust CLI tools: SVG word clouds, Typst data conversion, and Hanyu Pinyin sorting.

## Install

```bash
brew tap acture/ac
brew install char-cloud
```

You can also install directly with `brew install acture/ac/<formula>`.

## Choose a Tool

| Tool | Use it when | Install | Upstream |
| --- | --- | --- | --- |
| `char-cloud` | create shape-constrained SVG word clouds for reports, demos, and visual experiments | `brew install char-cloud` | [Acture/char-cloud](https://github.com/Acture/char-cloud) |
| `d2typ` | turn CSV/JSON/YAML/TOML/XLSX data into Typst-ready structures | `brew install d2typ` | [Acture/d2typ](https://github.com/Acture/d2typ) |
| `pinyin-sort` | sort Chinese text lists into predictable Hanyu Pinyin order for publishing and cleanup | `brew install pinyin-sort` | [Acture/pinyin-sort](https://github.com/Acture/pinyin-sort) |

## Example Preview

`char-cloud` preview, generated from a fixed-seed upstream example:

![char-cloud preview](assets/char-cloud-preview.svg)

`d2typ` in one pass:

```bash
$ d2typ examples/d2typ/input.json -o out.typ
$ cat out.typ
#let data = {count: 3, items: [svg, typst, pinyin], ready: true}
```

`pinyin-sort` for a quick cleanup:

```text
# input
张三
李四
王五

# output
李四
王五
张三
```

See the upstream repositories for complete flags, data format details, and extended examples.

## Why Trust This Tap

- Author-maintained formulae that track tagged upstream releases.
- CI audits the tap and build-tests the stable CLI installs on macOS and Linux.
- Smoke tests validate real output, not just `--version`.

## Notes

- This tap is for Homebrew users on macOS and Linux.
- Current formulae build from source with Rust, so first-time installs can take a little longer.
- Use `brew info <formula>` to inspect dependencies and caveats, and `brew upgrade` to pull newer releases.

## License

This tap is distributed under the [AGPL-3.0-only](LICENSE) license.
