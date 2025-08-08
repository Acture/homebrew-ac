class PinyinSort < Formula
  desc "Sorts Chinese strings by their Hanyu Pinyin (tone3) order"
  homepage "https://github.com/Acture/pinyin-sort"
  url "https://github.com/Acture/pinyin-sort/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "44f54d3869f07a7345f71c3b0a1e92ecc5b61fd639e2b6bb668db10aa45ea205"
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
    system bin/"pinyin-sort", "--version"
  end
end
