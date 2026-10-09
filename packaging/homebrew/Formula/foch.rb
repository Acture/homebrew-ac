require (Pathname(__FILE__).realpath.parent.parent/"lib/public_submodules_git_download_strategy").to_s

class Foch < Formula
  desc "EU4 mod analysis, merging and language server toolkit"
  homepage "https://github.com/Acture/foch"
  license all_of: ["AGPL-3.0-only", "GPL-3.0-only", "MIT"]
  head "https://github.com/Acture/foch.git",
       branch:            "master",
       using:             PublicSubmodulesGitDownloadStrategy,
       public_submodules: %w[src/packages/tree-sitter-paradox src/packages/foch/vendor/cwtools-eu4-config]

  depends_on "rust" => :build

  def install
    system "cargo", "install", *std_cargo_args(path: "src/apps/foch-cli"), "--bin", "foch"
    pkgshare.install "NOTICE.md", "LICENSE-MERGIRAF.txt"
  end

  test do
    ENV["HOME"] = testpath
    ENV["XDG_CONFIG_HOME"] = testpath/".config"
    (testpath/"local_patch/descriptor.mod").write 'name="Homebrew test"'
    (testpath/"foch.toml").write <<~TOML
      [project]
      game = "eu4"

      [[project.mods]]
      id = "local_patch"
      path = "local_patch"
    TOML

    output = shell_output("#{bin}/foch input inspect #{testpath}/foch.toml")
    assert_match "game: eu4", output
    assert_match "local_patch", output
    assert_match (testpath/"local_patch").to_s, output
    assert_match "cwt-schema", shell_output("#{bin}/foch --version")
  end
end
