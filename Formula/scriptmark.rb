class Scriptmark < Formula
  desc "Automated grading CLI for student programming assignments"
  homepage "https://github.com/Acture/scriptmark"
  license "GPL-3.0-or-later"

  depends_on "python@3.13"

  on_macos do
    on_arm do
      url "https://github.com/Acture/scriptmark/releases/download/v0.2.0/scriptmark-macos-aarch64",
          using: :nounzip
      sha256 "225ff894f026eddedeb4545160b6dc64540d6f16dafc3db93d8f7ca770b6424e"
    end
    on_intel do
      url "https://github.com/Acture/scriptmark/releases/download/v0.2.0/scriptmark-macos-x86_64",
          using: :nounzip
      sha256 "072bee4b00c09a5e6a3394d78e5071b284e3c97b33323c8c59528f6f5f9b2e02"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/Acture/scriptmark/releases/download/v0.2.0/scriptmark-linux-aarch64",
          using: :nounzip
      sha256 "30122edac25a8c9a75b042e516efc1255d6ac84eef14fc228eef0eac758a1a4d"
    end
    on_intel do
      url "https://github.com/Acture/scriptmark/releases/download/v0.2.0/scriptmark-linux-x86_64",
          using: :nounzip
      sha256 "7c70f0e735da3d3d370d0b9eaf46673b1ea9e757ed93a07e47fb489a48f5774e"
    end
  end

  def install
    libexec.install File.basename(stable.url) => "scriptmark"
    (libexec/"scriptmark").chmod 0555
    (bin/"scriptmark").write_env_script libexec/"scriptmark",
      PATH: "#{formula_opt_libexec("python@3.13")}/bin:$PATH"
  end

  test do
    (testpath/"submissions/alice_answer.py").write <<~PYTHON
      def add(a, b):
          return a + b
    PYTHON
    (testpath/"tests/add.toml").write <<~TOML
      [meta]
      name = "addition"
      file = "answer.py"
      function = "add"
      language = "python"

      [[cases]]
      name = "two integers"
      args = [2, 3]
      expect = 5
    TOML

    system bin/"scriptmark", "run", testpath/"submissions", "--tests", testpath/"tests",
      "--output", testpath/"results.json"
    reports = JSON.parse((testpath/"results.json").read)
    assert_equal 1, reports.length
    assert_equal "alice", reports.first.fetch("student_id")
    cases = reports.first.fetch("test_results").first.fetch("cases")
    assert_equal 1, cases.length
    assert_equal "passed", cases.first.fetch("status")
  end
end
