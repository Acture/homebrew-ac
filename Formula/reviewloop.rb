class Reviewloop < Formula
  desc "Reproducible, guardrailed automation for academic review workflows on paperreview.ai"
  homepage "https://github.com/Acture/reviewloop"
  url "https://github.com/Acture/reviewloop/archive/refs/tags/v0.1.4.tar.gz"
  sha256 "b53525b7c8f802925b297998c02044dac0e9fe03bf02ba2aa1bcafb426382736"
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
    ENV["OPENSSL_DIR"] = Formula["openssl@3"].opt_prefix if OS.linux?
    ENV["OPENSSL_NO_VENDOR"] = "1" if OS.linux?

    system "cargo", "install", *std_cargo_args(path: ".")
  end

  test do
    ENV["HOME"] = testpath
    ENV["XDG_CONFIG_HOME"] = testpath/".config"
    ENV["REVIEWLOOP_STATE_DIR"] = testpath/".review_loop"

    (testpath/"paper.pdf").write("%PDF-1.4\n")

    system bin/"reviewloop", "init"
    system bin/"reviewloop", "init", "project", "--project-id", "main"

    project_config_path = testpath/"reviewloop.toml"
    assert_path_exists project_config_path
    assert_includes project_config_path.read, "project_id = \"main\""

    system bin/"reviewloop", "--config", project_config_path,
      "paper", "add",
      "--paper-id", "main",
      "--pdf-path", testpath/"paper.pdf",
      "--backend", "stanford",
      "--no-submit-prompt"

    project_config = project_config_path.read
    assert_includes project_config, "id = \"main\""
    assert_includes project_config, "backend = \"stanford\""

    output = shell_output("#{bin}/reviewloop --config #{project_config_path} status --json")
    assert_match(/\[\]\s*\z/, output)
    assert_path_exists testpath/".review_loop/reviewloop.db"
  end
end
