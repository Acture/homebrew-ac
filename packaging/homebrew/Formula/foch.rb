class Foch < Formula
  desc "EU4 mod analysis, merging and language server toolkit"
  homepage "https://github.com/Acture/foch"
  url "https://github.com/Acture/foch/releases/download/v0.0.1/foch-0.0.1-source.tar.gz"
  sha256 "0503eba89f61eb86c62dea465bf42d480f2352358eca6527affd677fc5ed27ba"
  license all_of: ["AGPL-3.0-only", "GPL-3.0-only", "MIT"]

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
