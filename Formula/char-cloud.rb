class CharCloud < Formula
	desc "字符轮廓词云生成工具"
	homepage "https://github.com/acture/char-cloud"
	license "AGPL"
	if OS.mac? && Hardware::CPU.arm?
		url "https://github.com/acture/char-cloud/releases/download/v0.1.2/char-cloud-aarch64-macos"
		sha256 "afaa949f709eeb5e5816686145d9c9e6478557e60826eb3160daa46ce129075b"
	elsif OS.mac? && Hardware::CPU.intel?
		url "https://github.com/acture/char-cloud/releases/download/v0.1.2/char-cloud-x86_64-macos"
		sha256 "afaa949f709eeb5e5816686145d9c9e6478557e60826eb3160daa46ce129075b"
	elsif OS.linux? && Hardware::CPU.intel?
		url "https://github.com/acture/char-cloud/releases/download/v0.1.0/char-cloud-x86_64-linux"
		sha256 "60ee682691e429292e2329fc3dd81e54c549cefd05b85866b0b93fa545ec015b"
	elsif OS.windows? && Hardware::CPU.intel?
		url "https://github.com/acture/char-cloud/releases/download/v0.1.0/char-cloud-x86_64-windows.exe"
		sha256 "2c3850c505cc4463ff13eeceb63157cc715789bd0c831705ac032016f8e734da"
	else
		odie "Unsupported platform"
	end

	def install
		bin.install Dir["char-cloud*"].first => "char-cloud"
	end

	test do
		assert_match "Usage", shell_output("#{bin}/char-cloud --help")
	end
end