# /traviscontainerrunner/runner.py
#
# The main runner script, opens .travis.yml and then
# runs each command.
#
# See LICENCE.md for Copyright information

import os
import subprocess
import tempfile
import yaml

_CONTAINER_ONLY_ERROR = ("travis-container-runner only works with "
                         "containerized-scripts not allowing the "
                         "use of sudo."
                         ""
                         "Add sudo: false to your .travis.yml")


def main():
    """Runs the .travis.yml script."""

    with open(".travis.yml", "r") as yaml_file:
        travis_yaml = yaml.load(yaml_file.read())

        try:
            if travis_yaml["sudo"] is not False:
                raise RuntimeError(_CONTAINER_ONLY_ERROR)
        except KeyError:
            raise RuntimeError(_CONTAINER_ONLY_ERROR)

        script_commands = []

        for candidate_section in ["before_install",
                                  "install",
                                  "script",
                                  "before_cache",
                                  "after_success",
                                  "after_script",
                                  "before_deploy"]:
            try:
                script_commands += travis_yaml[candidate_section]
            except KeyError:
                continue

        with tempfile.NamedTemporaryFile(mode="wt",
                                         dir=os.getcwd()) as script_file:
            script_file.write("set -e\n")
            for command in script_commands:
                script_file.write("{0}\n".format(command))

            script_file.flush()
            return subprocess.check_call(["bash",
                                          "{0}".format(script_file.name)])
