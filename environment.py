import os

from conda_git_deployment import utils


root = os.path.dirname(__file__)
env = {}

# PYTHONPATH
env["PYTHONPATH"] = [
    os.path.join(root, "environment", "PYTHONPATH"),
]

# FTRACK_CONNECT_PLUGIN_PATH
env["FTRACK_CONNECT_PLUGIN_PATH"] = [
    os.path.join(os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-maya"),
    os.path.join(os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-nuke"),
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

utils.write_environment(env)
