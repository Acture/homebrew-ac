# typed: strict
# frozen_string_literal: true

# Fetch only the explicitly listed build dependencies, never private notes.
class PublicSubmodulesGitDownloadStrategy < GitDownloadStrategy
  private

  sig { override.returns(String) }
  def cache_tag
    "git-public-submodules"
  end

  sig { override.params(timeout: T.nilable(Time)).void }
  def update_submodules(timeout: nil)
    paths = T.cast(meta.fetch(:public_submodules, []), T::Array[String])
    return if paths.empty?

    command! "git", args: ["submodule", "sync", "--", *paths],
                    chdir: cached_location, timeout: Utils::Timer.remaining(timeout)
    command! "git", args: ["submodule", "update", "--init", "--checkout", "--", *paths],
                    chdir: cached_location, timeout: Utils::Timer.remaining(timeout)
    fix_absolute_submodule_gitdir_references!
  end
end
