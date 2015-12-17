# /traviscontainerrunner/runner.py
#
# The main runner script, opens .travis.yml and then
# runs each command.
#
# See LICENCE.md for Copyright information

import os
import subprocess
import tempfile
import sys
import yaml

_CONTAINER_ONLY_ERROR = ("travis-container-runner only works with "
                         "containerized-scripts not allowing the "
                         "use of sudo."
                         ""
                         "Add sudo: false to your .travis.yml")


class Cache(object):

    """Cache entry."""

    def __init__(self, line):
        """Initialize this cache entry."""
        super(Cache, self).__init__()

        components = line.split(" ")
        self.path = components[0]
        self.mtime = components[1]

    def __repr__(self):
        """Represent as string."""
        return self.path + " " + self.mtime

    def match(self, other):
        """Compare cache entry against the other checking if it is newer."""
        if self.path == other.path:
            return bool(self.mtime <= other.mtime)

        return False


def record_cache(travis_yaml):
    """Record caches."""

    if travis_yaml.get("cache", None):
        for cache_dir in travis_yaml["cache"].get("directories", list()):
            try:
                with open(".travis-runner-memo-" + cache_dir.replace("/", "_"),
                          "r") as f:
                    cache_file_entries = set([Cache(l) for l in f.readlines()])
            except IOError:
                cache_file_entries = set()

            current_cache_dir_entries = set()
            for root, _, filenames in os.walk(cache_dir):
                for filename in filenames:
                    path = os.path.join(root, filename).replace(" ", "_")
                    try:
                        mtime = os.stat(os.path.join(root, filename)).st_mtime
                    except OSError:
                        mtime = 1
                    line = "{0} {1}".format(path, mtime)
                    current_cache_dir_entries |= set([Cache(line)])

            for current_entry in current_cache_dir_entries:
                matching_entry_found = False

                for cache_entry in cache_file_entries:
                    if current_entry.match(cache_entry):
                        matching_entry_found = True
                        break
                if not matching_entry_found:
                    print("Would cache " + current_entry.path)

            with open(".travis-runner-memo-" + cache_dir.replace("/", "_"),
                      "w") as f:
                f.truncate(0)
                f.write("\n".join([repr(e) for e in current_cache_dir_entries]))


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

        sections = ["before_install",
                    "install",
                    "script",
                    "before_cache"]

        if len(sys.argv) > 1 and "--run-after-steps" in sys.argv:
            sections += ["after_success",
                         "after_script",
                         "before_deploy"]

        for candidate_section in sections:
            try:
                script_commands += (travis_yaml[candidate_section] or list())
            except KeyError:
                continue

        with tempfile.NamedTemporaryFile(mode="wt",
                                         dir=os.getcwd()) as script_file:
            script_file.write("set -e\n")
            for command in script_commands:
                script_file.write("{0}\n".format(command))

            script_file.flush()
            result = subprocess.check_call(["bash",
                                            "{0}".format(script_file.name)])

            if result != 0:
                return result

            if len(sys.argv) > 1 and "--check-cache" in sys.argv:
                record_cache(travis_yaml)
