import os
import subprocess
import shutil
import sys

from conda_git_deployment import utils


root = os.path.dirname(__file__)
env = {}


def build_rv_plugin():

    subprocess.call(
        ["python", "setup.py", "build_plugin"],
        cwd=os.path.join(
            os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-rv"
        )
    )

    # Clear existing plugin
    path = os.path.join(root, "environment", "RV_SUPPORT_PATH")
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

    # Copy build plugin
    sys.path.append(
        os.path.join(
            os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-rv", "source"
        )
    )
    import ftrack_connect_rv
    rvpkg_version = '.'.join(ftrack_connect_rv.__version__.split('.'))
    plugin_file = 'ftrack-{0}.rvpkg'.format(rvpkg_version)
    src = os.path.join(
        os.environ["CONDA_GIT_REPOSITORY"],
        "ftrack-connect-rv",
        "build",
        plugin_file
    )
    dst = os.path.join(
        root, "environment", "RV_SUPPORT_PATH", "Packages", plugin_file
    )

    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))

    shutil.move(src, dst)


# Build RV plugin if updating the repositories
if ("CONDA_GIT_UPDATE" in os.environ and
   "repositories" in os.environ["CONDA_GIT_UPDATE"]):
    build_rv_plugin()

# Build RV plugin if none exists
if not os.path.exists(os.path.join(root, "environment", "RV_SUPPORT_PATH")):
    build_rv_plugin()

# PYTHONPATH
env["PYTHONPATH"] = [os.path.join(root, "environment", "PYTHONPATH")]

# FTRACK_CONNECT_PLUGIN_PATH
env["FTRACK_CONNECT_PLUGIN_PATH"] = [
    os.path.join(os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-maya"),
    os.path.join(os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-nuke"),
    os.path.join(os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-rv"),
    os.path.join(
        os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-nuke-studio"
    ),
    os.path.join(root, "environment", "FTRACK_CONNECT_PLUGIN_PATH"),
]

# FTRACK_CONNECT_MAYA_PLUGINS_PATH
env["FTRACK_CONNECT_MAYA_PLUGINS_PATH"] = [
    os.path.join(
        os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-maya", "resource"
    )
]

# FTRACK_CONNECT_NUKE_PLUGINS_PATH
env["FTRACK_CONNECT_NUKE_PLUGINS_PATH"] = [
    os.path.join(
        os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-nuke", "resource"
    )
]

# FTRACK_CONNECT_NUKE_STUDIO_PATH
env["FTRACK_CONNECT_NUKE_STUDIO_PATH"] = [
    os.path.join(
        os.environ["CONDA_GIT_REPOSITORY"],
        "ftrack-connect-nuke-studio",
        "resource"
    )
]

# QT_PREFERRED_BINDING
env["QT_PREFERRED_BINDING"] = ["PySide2", "PySide"]

# RV_SUPPORT_PATH
env["RV_SUPPORT_PATH"] = [os.path.join(root, "environment", "RV_SUPPORT_PATH")]

utils.write_environment(env)
