import subprocess
import os
import shutil
import sys

from conda_git_deployment import utils


def _build_rv_plugin():
    root = os.path.dirname(__file__)

    repository_path = os.path.abspath(
        os.path.join(
            sys.executable,
            "..",
            "Lib",
            "site-packages",
            "repositories",
            "ftrack-connect-rv"
        )
    )

    subprocess.call(
        ["python", "setup.py", "build_plugin"],
        cwd=repository_path
    )

    # Clear existing plugin
    path = os.path.join(root, "environment", "RV_SUPPORT_PATH")
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

    # Copy build plugin
    sys.path.append(os.path.join(repository_path, "source"))
    import ftrack_connect_rv
    rvpkg_version = '.'.join(ftrack_connect_rv.__version__.split('.'))
    plugin_file = 'ftrack-{0}.rvpkg'.format(rvpkg_version)
    src = os.path.join(repository_path, "build", plugin_file)
    dst = os.path.join(
        root, "environment", "RV_SUPPORT_PATH", "Packages", plugin_file
    )

    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))

    shutil.move(src, dst)


def build_rv_plugin():
    # Check is ftrack_connect_rv is available for building plugin.
    if utils.check_module("ftrack_connect_rv"):
        # Build RV plugin if updating the repositories
        if ("CONDA_GIT_UPDATE" in os.environ and
           "repositories" in os.environ["CONDA_GIT_UPDATE"]):
            _build_rv_plugin()

        # Build RV plugin if none exists
        path = os.path.join(
            os.path.dirname(__file__), "environment", "RV_SUPPORT_PATH"
        )
        if not os.path.exists(path):
            _build_rv_plugin()
    else:
        msg = "Could not build ftrack-connect-rv plugin because "
        msg += "ftrack_connect_rv in not available."
        print msg


def build_ftrack_connect_resources():
    # Build ftrack-connect resources
    resources = os.path.join(
        os.environ["CONDA_GIT_REPOSITORY"],
        "ftrack-connect",
        "source",
        "ftrack_connect",
        "ui",
        "resource.py"
    )
    if not os.path.exists(resources):
        subprocess.call(
            [
                "python",
                os.path.join(
                    os.environ["CONDA_GIT_REPOSITORY"],
                    "ftrack-connect",
                    "setup.py"
                ),
                "build_resources"
            ]
        )


if __name__ == "__main__":
    build_rv_plugin()
    build_ftrack_connect_resources()
