from git import Repo
from functools import partial

def branch_message(branch_name=None, message=None):
    return "Branch {} is {}".format(branch_name, message)

def main():
    repo = Repo(path="/tmp/test")
    git = repo.git

    #for branch in repo.branches:
    branch = repo.branches[1]

    current_branch_message = partial(branch_message, branch.name)
    tracking_branch = branch.tracking_branch()

    if not tracking_branch:
        print(current_branch_message("not tracked by any remote"))

    ble = "{local}...{tracking}".format(local=branch.name, tracking=tracking_branch.name)
    sru = git.rev_list(ble, count=True, left_right=True).split("\t")
    ahead, behind = map(int, sru)

    assert ahead >= 0
    assert behind >= 0

    if ahead:
        print(current_branch_message("ahead of tracking branch by {} commits".format(ahead)))
    if behind:
        print(current_branch_message("behind of tracking branch by {} commits".format(behind)))

main()
