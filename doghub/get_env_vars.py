import os  # flake8: noqa
import subprocess
import ast
from pathlib import Path  # noqa: F401


def get_environ_vars() -> None:
    """adds AWS EB Environment Properties as Env vars"""
    completed_process = subprocess.run(
        ["/opt/elasticbeanstalk/bin/get-config", "environment"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    return ast.literal_eval(completed_process.stdout)


def update_os_environ():
    if "RDS_HOSTNAME" in os.environ:
        os.environ.update(get_environ_vars())
    return None
