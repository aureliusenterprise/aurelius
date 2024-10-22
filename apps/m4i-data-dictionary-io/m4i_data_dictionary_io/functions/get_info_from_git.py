import git
from typing import Tuple


def get_info_from_git(file_location: str) -> Tuple[str, str]:
    """Return local branch and version with local version identifier - Based on File System"""
    repo = git.Repo(file_location)
    local_branch = repo.active_branch.name
    sha = repo.head.object.hexsha[0:8]
    if repo.is_dirty():
        return local_branch, '{sha}.dirty'.format(sha=sha)
    else:
        return local_branch, '{sha}'.format(sha=sha)
    return local_branch, "no_version"
# END get_info_from_git
