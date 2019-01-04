from functools import partial

from git import Repo


def main():
    repo = Repo(path="/tmp/test")

    for branch in repo.branches:
        branch_information = get_branch_information(branch)
        branch_information.output_messages()


class BranchReport:
    def __init__(self):
       self.messages = [] 

    def add_message(self, message):
        self.messages.append(message)

    def output_messages(self, fn=print):
        for message in self.messages:
            fn(message)


def get_branch_information(branch):
    current_branch_message = partial(branch_message, branch.name)
    tracking_branch = branch.tracking_branch()
    git_cmd = branch.repo.git
    report = BranchReport()

    if not tracking_branch:
        report.add_message(current_branch_message("not tracked"))
    else:
        branches_to_compare = "{local}...{tracking}".format(local=branch.name, tracking=tracking_branch.name)
        ahead, behind = intify(git_cmd.rev_list(branches_to_compare, count=True, left_right=True).split("\t"))
        assert ahead >= 0
        assert behind >= 0

        if ahead:
            report.add_message(current_branch_message("ahead of tracking branch by {} commit{}".format(ahead, "s" if ahead > 1 else "")))
        if behind:
            report.add_message(current_branch_message("behind of tracking branch by {} commit{}".format(behind, "s" if ahead > 1 else "")))

    return report


def branch_message(branch_name=None, message=None):
    return "Branch {} is {}".format(branch_name, message)

intify = partial(map, int)

if __name__ == "__main__":
    main()
