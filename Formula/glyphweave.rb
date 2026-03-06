class Glyphweave < Formula
  desc "Generate shape-constrained SVG word clouds"
  homepage "https://github.com/Acture/glyphweave"
  url "https://github.com/Acture/glyphweave/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "f4e78856382440f6ed3824b748b4a501051f3f381e7e4f496f3ef0fc6e88fd59"
  license "AGPL-3.0-only"

  livecheck do
    url :stable
    regex(/^v?(\d+(?:\.\d+)+)$/i)
  end

  depends_on "rust" => :build

  def install
    system "cargo", "install", *std_cargo_args

    legacy_binary = bin/"char-cloud"
    # v0.2.0 still installs the old executable name from the tagged source.
    if legacy_binary.exist? && !(bin/"glyphweave").exist?
      legacy_binary.rename bin/"glyphweave"
    end
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
