class CharCloud < Formula
  desc "Generate a high-density, shape-fitting word cloud in SVG format"
  homepage "https://github.com/Acture/char-cloud"
  url "https://github.com/Acture/char-cloud/archive/refs/tags/v0.1.2.tar.gz"
  sha256 "c7bdf909266d4eb43938b019eb8aa8616ef89dfb138c90ee7b6c3ff22e4e473b"
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
    system bin/"char-cloud", "--version"
  end
end
