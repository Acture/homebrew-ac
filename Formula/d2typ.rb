class D2typ < Formula
  desc "Convert structured data into Typst syntax for embedding in documents"
  homepage "https://github.com/Acture/d2typ"
  url "https://github.com/Acture/d2typ/archive/refs/tags/v0.1.3.tar.gz"
  sha256 "800113dcc8eb320557ce22ebbf69729059356a265c5f0f95515bae7193b2860a"
  license "AGPL-3.0-only"

  livecheck do
    url :stable
    regex(/^v?(\d+(?:\.\d+)+)$/i)
  end

  depends_on "rust" => :build

  def install
    system "cargo", "install", *std_cargo_args
  end

  test do
    system bin/"d2typ", "--version"
  end
end
