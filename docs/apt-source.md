# Acture APT source

This is the implementation for the shared Debian 13 / Ubuntu 24.04 source,
covering amd64 and arm64. It is not live yet. GitHub Pages is configured at
`https://acture.github.io/homebrew-ac/`. Official distribution inclusion is a
later task.

The dedicated RSA 3072 archive key has the full fingerprint
`D95016A338D84A5C48B48405DEE6329179875340` and expires on 2028-10-03.
The [reviewed public key](../packaging/apt/acture-archive-keyring.asc) is committed
here; private-key material and its passphrase stay outside Git. Renew or rotate
the archive key before expiry, publishing the new fingerprint before changing
the signing identity.

`packaging/apt/releases.json` is the approved upstream release ledger. Each
entry pins a repository, tag, full commit, Debian version and architectures.
The first entry expects devtunnel-service v0.1.0 at a78fc33. That tag and release
must be published before the source can fetch it. Add trapi2litellm only after
its distribution packages have passed their own acceptance.

The builder downloads the `.deb` assets and `SHA256SUMS` from each stable
GitHub Release, checks the tag's commit and package checksums, and compares
the package's actual name/version/architecture with the ledger. It creates
`pool/`, per-architecture compressed `Packages` indexes, `Release`, signed
`InRelease` and `Release.gpg`, a minimal public key, and a deb822 `.sources` file.
All build outputs stay in `dist/`.

## Publishing

The publication workflow runs only from `master`, manually or weekly. It
restores the last successful publication's snapshot, checks its signature and
fingerprint, and preserves older packages and by-hash indexes. Replacing a
package's bytes without changing its version is refused. Signed metadata
expires after 14 days; weekly publication refreshes it. Monitor failed scheduled
runs so the source does not expire.

The workflow installs from the signed snapshot inside fresh Debian and Ubuntu
containers before deploying a complete GitHub Pages artifact. A failed build
or pre-deployment install leaves the last deployed site intact. After deployment,
a separate four-target HTTPS acceptance workflow installs from the actual
endpoint using the accepted snapshot's public key. A failure there requires
investigation; it does not automatically roll back Pages. Confirm both the
publication and live acceptance runs before advertising the source. GitHub Pages
has a 1 GB site limit; move to object storage before approaching it.

Before the first deployment:

1. Publish the pinned upstream tag/release after its product acceptance passes.
2. Generate a dedicated passphrase-protected repository signing key. Keep a
   secure offline copy; do not reuse a personal Git signing key. Review and
   publish its full fingerprint.
3. Configure `APT_SIGNING_KEY` (armored private key) and
   `APT_SIGNING_PASSPHRASE` as Actions secrets in this repository.
4. Configure `APT_SIGNING_FINGERPRINT` (full uppercase fingerprint) and
   `APT_REPOSITORY_URI` as Actions variables.
5. Enable GitHub Pages with the Actions publishing source and review the
   `github-pages` environment's deployment protections.
6. Merge the reviewed implementation, then run `Publish APT source`.
7. Verify signature checking, installation and upgrade through the actual HTTPS
   endpoint on each target distribution/architecture before advertising it.

Production key generation and secret configuration are deliberate setup actions;
the build does not create a production key or enable Pages automatically.
Private keys are imported only into the runner's temporary GnuPG directory and
removed after the build. Signing requires the configured full fingerprint.

As of 2026-10-04, the signing identity, Actions secrets/variables and Pages
Actions source are configured. The pinned upstream release, merging this
implementation and the first deployment remain pending. The public-key
bootstrap includes the reviewed fingerprint independently of the downloaded
key's own description.

## User installation after publication

These commands are for **after** the live URL and fingerprint are confirmed.
The fingerprint is pinned to the reviewed archive key:

```fish
set apt_uri https://acture.github.io/homebrew-ac
set expected_fingerprint D95016A338D84A5C48B48405DEE6329179875340
sudo apt update; or exit 1
sudo apt install -y ca-certificates curl gnupg; or exit 1
curl -fsSL "$apt_uri/acture-archive-keyring.asc" -o acture-archive-keyring.asc; or exit 1
set downloaded_fingerprint (gpg --batch --with-colons --show-keys acture-archive-keyring.asc | awk -F: '$1 == "fpr" { print $10; exit }')
test "$downloaded_fingerprint" = "$expected_fingerprint"; or exit 1
sudo install -D -m 0644 acture-archive-keyring.asc /etc/apt/keyrings/acture-archive-keyring.asc; or exit 1
printf 'Types: deb\nURIs: %s/\nSuites: stable\nComponents: main\nArchitectures: amd64 arm64\nSigned-By: /etc/apt/keyrings/acture-archive-keyring.asc\n' "$apt_uri" | sudo tee /etc/apt/sources.list.d/acture.sources >/dev/null; or exit 1
sudo apt update; or exit 1
sudo apt install devtunnel-service
```

APT installs the command. The product's explicit deployment, service-start,
authentication and lingering rules remain in its own documentation. Package
updates then use normal APT upgrades. Do not set `trusted=yes` or disable
signature checking.

## Development and acceptance

```fish
uv run --directory packaging/apt --locked ruff check .
uv run --directory packaging/apt --locked ruff format --check .
uv run --directory packaging/apt --locked ty check .
python3 -m unittest discover --start-directory packaging/apt -v
```

`APT source CI` runs the suite on Debian 13 and Ubuntu 24.04, on native amd64
and arm64 runners. It checks real Signed-By installation and upgrade, rejects
tampered signatures, prevents replacement of an existing package version and
filters architecture-specific packages. Its probe installs into an isolated
dpkg root, not the machine's system database. The Linux tests explicitly skip
when the required APT build tools are unavailable.

The last publication's artifact is retained for 90 days. Weekly refresh keeps
it available. If it expires, publication fails rather than silently losing old
packages or by-hash indexes; restore a verified snapshot before republishing.

References: [APT archive authentication](https://manpages.debian.org/trixie/apt/apt-secure.8.en.html),
[GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
