class Docpack < Formula
  desc "Freeze structured data into document-native modules"
  homepage "https://github.com/Acture/docpack"
  url "https://github.com/Acture/docpack/archive/refs/tags/v0.2.1.tar.gz"
  sha256 "dc1fc1479312315f11c8e0f9b498019b702652daa10b8d5a30e11bee226fe6a2"
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

    output = shell_output("#{bin}/docpack emit #{testpath/"input.json"} --backend typst")
    assert_match "#let input", output
    assert_match "\"count\": 3", output
    assert_match "\"ready\": true", output
  end
end
