class Reviewloop < Formula
  desc "Reproducible, guardrailed automation for academic review workflows on paperreview.ai"
  homepage "https://github.com/Acture/reviewloop"
  url "https://github.com/Acture/reviewloop/archive/refs/tags/v0.1.3.tar.gz"
  sha256 "a130e82b5dd81752c23398f883e2e6f32cadc27fed37ad38150ff09a81320b71"
  license "GPL-3.0-only"

  livecheck do
    url :stable
    regex(/^v?(\d+(?:\.\d+)+)$/i)
  end

  depends_on "rust" => :build

  on_linux do
    depends_on "openssl@3"
    depends_on "pkgconf" => :build
  end

  def install
    ENV["OPENSSL_DIR"] = Formula["openssl@3"].opt_prefix if OS.linux?
    ENV["OPENSSL_NO_VENDOR"] = "1" if OS.linux?

    system "cargo", "install", "--locked", *std_cargo_args(path: ".")
  end

  test do
    ENV["HOME"] = testpath
    ENV["XDG_CONFIG_HOME"] = testpath/".config"
    ENV["REVIEWLOOP_STATE_DIR"] = testpath/".review_loop"

    (testpath/"paper.pdf").write("%PDF-1.4\n")
    (testpath/"reviewloop-test.toml").write <<~TOML
      [logging]
      output = "file"
    TOML

    system bin/"reviewloop", "--config", testpath/"reviewloop-test.toml",
      "paper", "add",
      "--paper-id", "main",
      "--pdf-path", testpath/"paper.pdf",
      "--backend", "stanford",
      "--no-submit-prompt"

    config_path = testpath/".config/reviewloop/reviewloop.toml"
    assert_path_exists config_path
    assert_includes config_path.read, "[providers.stanford]"

    output = shell_output("#{bin}/reviewloop --config #{testpath/"reviewloop-test.toml"} status --json")
    assert_equal "[]\n", output
    assert_path_exists testpath/".review_loop/reviewloop.db"
  end
end
