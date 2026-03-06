class Reviewloop < Formula
  desc "Durable CLI/daemon for paperreview.ai submission and review retrieval"
  homepage "https://github.com/Acture/review-loop"
  url "https://github.com/Acture/review-loop/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "bad77e3bafe8e9fe9672a51ec8dcd0b4a3baf5bf482d6cd2cd82fdb31b6f7088"
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

    system "cargo", "install", "--locked", *std_cargo_args
  end

  test do
    ENV["HOME"] = testpath
    ENV["XDG_CONFIG_HOME"] = testpath/".config"

    (testpath/"paper.pdf").write("%PDF-1.4\n")
    (testpath/"reviewloop-test.toml").write <<~TOML
      [logging]
      output = "file"
    TOML

    system bin/"reviewloop", "--config", testpath/"reviewloop-test.toml",
      "paper", "add",
      "--paper-id", "main",
      "--path", testpath/"paper.pdf",
      "--backend", "stanford",
      "--watch", "false",
      "--no-submit-prompt"

    config_path = testpath/".config/reviewloop/reviewloop.toml"
    assert_path_exists config_path
    assert_match 'id = "main"', config_path.read
    assert_match 'backend = "stanford"', config_path.read

    output = shell_output("#{bin}/reviewloop --config #{testpath/"reviewloop-test.toml"} status --json")
    assert_equal "[]\n", output
    assert_path_exists testpath/".review_loop/reviewloop.db"
  end
end
