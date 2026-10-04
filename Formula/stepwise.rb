require_relative "../packaging/lib/public_submodules_git_download_strategy"

class Stepwise < Formula
  desc "Interactive Python evaluation and propositional logic exercises"
  homepage "https://github.com/Acture/Stepwise"
  license "AGPL-3.0-only"
  head "https://github.com/Acture/Stepwise.git", branch: "master",
                                                 using:  PublicSubmodulesGitDownloadStrategy

  depends_on "rust" => :build

  def install
    system "cargo", "install", *std_cargo_args(path: ".")
  end

  test do
    assert_match "完成：7", shell_output("#{bin}/stepwise --python '1 + 2 * 3' --trace")
    assert_equal "等价：所有赋值下真值相同。\n",
      shell_output("#{bin}/stepwise --logic 'P & Q' --equivalent 'Q & P'")
  end
end
