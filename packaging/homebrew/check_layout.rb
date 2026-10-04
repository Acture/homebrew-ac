# typed: strict
# frozen_string_literal: true

# Run with `brew ruby packaging/homebrew/check_layout.rb`.
root = T.let(Pathname(__dir__).realpath.parent.parent, Pathname)

%w[Formula Aliases].each do |name|
  entry = T.let(root/name, Pathname)
  expected = T.let(Pathname("packaging/homebrew")/name, Pathname)
  raise "#{name} must be a directory symlink" unless entry.symlink?
  raise "#{name} must link to #{expected}" if entry.readlink != expected
  raise "#{name} resolves outside its channel directory" if entry.realpath != (root/expected).realpath
end

formulae = T.let((root/"Formula").glob("**/*.rb"), T::Array[Pathname])
raise "No active Homebrew formulae found" if formulae.empty?

aliases = T.let((root/"Aliases").children, T::Array[Pathname])
targets = T.let(formulae.map(&:realpath), T::Array[Pathname])
aliases.each do |path|
  raise "#{path.basename} must be a symlink" unless path.symlink?
  raise "#{path.basename} must alias an active formula" unless targets.include?(path.realpath)
end

if (tap = Tap.from_path(root))
  discovered = T.let(tap.formula_files.map(&:realpath).sort, T::Array[Pathname])
  raise "Homebrew discovery differs from the channel contents" if discovered != targets.sort
end

puts "Verified Homebrew directory links, #{formulae.length} formulae and #{aliases.length} aliases"
