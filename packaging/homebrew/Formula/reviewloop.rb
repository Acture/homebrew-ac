class Reviewloop < Formula
  desc "Durable automation for academic review workflows on paperreview.ai"
  homepage "https://github.com/Acture/reviewloop"
  url "https://github.com/Acture/reviewloop/archive/refs/tags/v0.2.1.tar.gz"
  sha256 "d030fe258caf5c1f326225c9c7b57bd2c283ecab86790f9e8c145f4c6d3a1b52"
  license "GPL-3.0-only"

  livecheck do
    url :stable
    regex(/^v?(\d+(?:\.\d+)+)$/i)
  end

  depends_on "rust" => :build

  on_linux do
    depends_on "pkgconf" => :build
    depends_on "openssl@3"
  end

  def install
    ENV["OPENSSL_DIR"] = formula_opt_prefix("openssl@3") if OS.linux?
    ENV["OPENSSL_NO_VENDOR"] = "1" if OS.linux?

    system "cargo", "install", *std_cargo_args(path: ".")
  end

  test do
    ENV["HOME"] = testpath
    ENV["XDG_CONFIG_HOME"] = testpath/".config"
    ENV["REVIEWLOOP_STATE_DIR"] = testpath/".review_loop"

    system bin/"reviewloop", "init"
    config_path = testpath/".config/reviewloop/config.toml"
    assert_path_exists config_path
    assert_includes config_path.read, "[providers.stanford]"
    config_path.atomic_write <<~TOML
      [logging]
      output = "stderr"
    TOML

    project_path = testpath/"reviewloop.toml"
    system bin/"reviewloop", "--config", project_path, "init", "project", "--project-id", "main"
    assert_path_exists project_path
    assert_includes project_path.read, 'project_id = "main"'

    (testpath/"paper.pdf").write("%PDF-1.4\n")
    system bin/"reviewloop", "--config", project_path,
      "paper", "add",
      "--paper-id", "main",
      "--pdf-path", testpath/"paper.pdf",
      "--backend", "stanford",
      "--no-submit-prompt"

    assert_includes project_path.read, "[[papers]]"
    assert_match(/^id = "main"$/, project_path.read)

    output = JSON.parse(shell_output("#{bin}/reviewloop --config #{project_path} status --json"))
    assert_equal "main", output.fetch("project_id")
    assert_empty output.fetch("papers")
    assert_path_exists testpath/".review_loop/reviewloop.db"
  end
end
