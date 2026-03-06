class Reviewloop < Formula
  desc "Reproducible, guardrailed automation for academic review workflows on paperreview.ai"
  homepage "https://github.com/Acture/review-loop"
  url "https://crates.io/api/v1/crates/reviewloop/0.1.1/download"
  sha256 "6f440bf6baf457edfbcb719f49fc9c9ec79cdd6311901a77149ab36b24374d5b"
  license "GPL-3.0-only"
  version "0.1.1"
  depends_on "rust" => :build

  def install
    system "cargo", "install", *std_cargo_args
  end

  test do
    assert_match "0.1.1", shell_output("#{bin}/reviewloop --version")
  end
end
