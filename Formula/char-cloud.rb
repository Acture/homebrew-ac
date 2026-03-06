class CharCloud < Formula
  desc "Generate a high-density, shape-fitting word cloud in SVG format"
  homepage "https://github.com/Acture/char-cloud"
  url "https://github.com/Acture/char-cloud/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "8a9b4f494701fc3afaf99c7ae74c96472e0934de5d6fccfc119b74ad413f82bc"
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
