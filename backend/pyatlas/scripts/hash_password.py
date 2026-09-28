"""Print a users-credentials.properties line with a BCrypt password hash (like Atlas' UserDao.encrypt).

    python scripts/hash_password.py alice DATA_STEWARD
    -> alice=DATA_STEWARD::$2b$12$....
"""
import getpass
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pyatlas.auth import hash_password  # noqa: E402


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: hash_password.py <user> [GROUP1,GROUP2]")
    user, groups = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
    pw = getpass.getpass(f"password for {user}: ")
    if pw != getpass.getpass("repeat: "):
        sys.exit("passwords differ")
    print(f"{user}={groups}::{hash_password(pw)}")


if __name__ == "__main__":
    main()
