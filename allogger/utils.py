import os

from . import get_logger

root = get_logger('root')

def report_env(to_stdout=False):
    from git import Repo, InvalidGitRepositoryError
    from socket import gethostname
    from getpass import getuser

    root.info(f'Running on {gethostname()} as {getuser()}', to_stdout=to_stdout)

    project_path = os.path.dirname(os.path.realpath(__file__))
    try:
        repo = Repo(project_path, search_parent_directories=True)
        active_branch = repo.active_branch
        latest_commit = repo.commit(active_branch)
        latest_commit_sha = latest_commit.hexsha
        latest_commit_sha_short = repo.git.rev_parse(latest_commit_sha, short=6)
        root.info(f'We are on branch {active_branch} using commit {latest_commit_sha_short}', to_stdout=to_stdout)
    except InvalidGitRepositoryError:
        root.info(f'{project_path} is not a git repo', to_stdout=to_stdout)

    root.info(f'Saving data to {root.logdir}', to_stdout=to_stdout)