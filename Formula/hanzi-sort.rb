class HanziSort < Formula
  desc "Sort Chinese text by pinyin or stroke count"
  homepage "https://github.com/Acture/hanzi-sort"
  url "https://github.com/Acture/hanzi-sort/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "b08b83f9bac7628d1404fa93358f057dc5ff5b729352fc36069fb0f2c7e22e3b"
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
    pinyin_output = shell_output("#{bin}/hanzi-sort -t 张三 李四 王五")

    assert_match "李四", pinyin_output
    assert_match "王五", pinyin_output
    assert_match "张三", pinyin_output
    assert_operator pinyin_output.index("李四"), :<, pinyin_output.index("王五")
    assert_operator pinyin_output.index("王五"), :<, pinyin_output.index("张三")

    strokes_output = shell_output("#{bin}/hanzi-sort -t 天 一 十 --sort-by strokes --columns 1 --entry-width 2 --blank-every 0")
    assert_operator strokes_output.index("一"), :<, strokes_output.index("十")
    assert_operator strokes_output.index("十"), :<, strokes_output.index("天")
  end
end
