import os
import sys

branches = ["asaf", "kirsh", " evyatar", "avihai", "shani"]


def execute(cmd: str):
    print(cmd)
    os.system(cmd)


def for_branch(*commands: str):
    for branch in branches:
        execute(f"git checkout {branch}")
        for cmd in commands:
            execute(cmd.replace("<branch>", branch))


def pull():
    for_branch("git pull")


def push():
    for_branch("git push")


def rebase(to: str):
    for_branch("git pull", f"git rebase {to}", "git push")


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "pull":
        pull()
    elif command == "push":
        push()
    elif command == "rebase":
        rebase("master")
    execute("git checkout master")