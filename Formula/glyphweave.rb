class Glyphweave < Formula
  desc "Shape-constrained SVG word clouds, built for speed"
  homepage "https://github.com/Acture/glyphweave"
  url "https://github.com/Acture/glyphweave/archive/refs/tags/v0.3.0.tar.gz"
  sha256 "c6ea5cf6fb7dfbc3726c3ffacc54f83b0738f16781b6a9a998fc1e8098ace1a0"
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
    assert font, "No suitable system font found for glyphweave test"

    (testpath/"words.txt").write("cloud,3\nsvg,2\nlayout\n")
    output = testpath/"out.svg"

    system bin/"glyphweave", "--text", "AI",
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
