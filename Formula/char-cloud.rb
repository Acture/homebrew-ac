class CharCloud < Formula
  desc "Generate dense SVG word clouds that fit a target shape"
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
    font = [
      "/Library/Fonts/NotoSansSC-Regular.ttf",
      "/Library/Fonts/SourceHanSansSC-Regular.otf",
      "/System/Library/Fonts/Supplemental/Arial.ttf",
      "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf",
      "/usr/share/fonts/opentype/noto/NotoSansSC-Regular.otf",
      "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ].find { |path| File.exist?(path) }
    assert font, "No suitable system font found for char-cloud test"

    (testpath/"words.txt").write("cloud,3\nsvg,2\nlayout\n")
    output = testpath/"out.svg"

    system bin/"char-cloud", "--text", "AI",
                              "--word-file", testpath/"words.txt",
                              "--algorithm", "fast-grid",
                              "--seed", "7",
                              "--font", font,
                              "--no-progress",
                              "--output", output
    assert_predicate output, :exist?
    assert_match "<svg", output.read
  end
end
