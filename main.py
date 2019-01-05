import sys
from functools import partial

from git import Repo
from git.exc import InvalidGitRepositoryError


def main(print_function=print, input_function=sys.stdin.readlines):
    padded_print_function = partial(print_function, "\t")

    for raw_repo_path in input_function():
        repo_path = raw_repo_path.rstrip()

        if not repo_path: # deals with a single \n at the end of a file
            break

        try:
            repo = Repo(path=repo_path)
        except InvalidGitRepositoryError as e:
            print_function("Path {} is not a valid git repo".format(e))
        else:
            branch_reports = [get_branch_information(branch) for branch in repo.branches]

            if branch_reports and any((bool(report) for report in branch_reports)):
                print_function("In repo {}:".format(repo_path))
                for branch_report in branch_reports:
                    for message in branch_report.messages:
                        padded_print_function(message)


class BranchReport:
    def __init__(self):
       self._messages = [] 

    @property
    def messages(self):
        return self._messages

    def add_message(self, message):
        self.messages.append(message)

    def __bool__(self):
        return bool(self._messages)

def get_branch_information(branch):
    report = BranchReport()

    current_branch_message = partial(branch_message, branch.name)
    git_cmd = branch.repo.git
    tracking_branch = branch.tracking_branch()

    if not tracking_branch:
        report.add_message(current_branch_message("is not tracked"))
        return report

    if tracking_branch not in branch.repo.refs:
        report.add_message(current_branch_message("has tracking branch set, yet the tracking branch itself is missing"))
        return report

    branches_to_compare = "{local}...{tracking}".format(local=branch.name, tracking=tracking_branch.name)
    ahead, behind = intify(git_cmd.rev_list(branches_to_compare, count=True, left_right=True).split("\t"))
    assert ahead >= 0
    assert behind >= 0

    if ahead:
        report.add_message(current_branch_message("is ahead of the tracking branch by {} commit{}".format(ahead, "s" if ahead > 1 else "")))
    if behind:
        report.add_message(current_branch_message("is behind the tracking branch by {} commit{}".format(behind, "s" if ahead > 1 else "")))

    return report

def branch_message(branch_name=None, message=None):
    return "Branch {} {}".format(branch_name, message)

intify = partial(map, int)

if __name__ == "__main__":
    main()
