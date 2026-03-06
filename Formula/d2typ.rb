class D2typ < Formula
  desc "Convert structured data into Typst-ready syntax for documents"
  homepage "https://github.com/Acture/d2typ"
  url "https://github.com/Acture/d2typ/archive/refs/tags/v0.1.3.tar.gz"
  sha256 "13b990ed848848de00e8c5c54c5874954404ef3ebc74b8202cce4ab366da87df"
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
    (testpath/"input.json").write <<~JSON
      {"count":3,"items":[1,2,3],"ready":true}
    JSON

    output = testpath/"out.typ"
    system bin/"d2typ", testpath/"input.json", "-o", output

    rendered = output.read
    assert_match "#let data", rendered
    assert_match "count: 3", rendered
    assert_match "ready: true", rendered
  end
end
