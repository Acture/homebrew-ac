class HanziSort < Formula
  desc "Sort Chinese text by pinyin or stroke count"
  homepage "https://github.com/Acture/hanzi-sort"
  url "https://github.com/Acture/hanzi-sort/archive/refs/tags/v0.2.3.tar.gz"
  sha256 "79498719f932410aca95c18adc3bdc0567fc87f7b4d7d9952bfe4a9ffbbe8e77"
  license "AGPL-3.0-only"

  livecheck do
    url :stable
    regex(/^v?(\d+(?:\.\d+)+)$/i)
  end

  depends_on "rust" => :build

  def install
    system "cargo", "install", *std_cargo_args, "--all-features"
  end

  test do
    output = shell_output("#{bin}/hanzi-sort -t 张三 李四 王五")

    assert_match "李四", output
    assert_match "王五", output
    assert_match "张三", output
    assert_operator output.index("李四"), :<, output.index("王五")
    assert_operator output.index("王五"), :<, output.index("张三")
  end
end
