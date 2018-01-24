import os

from conda_git_deployment import utils
import environment_setup


def main():
    root = os.path.dirname(__file__)
    env = {}

    # FTRACK_CONNECT_PLUGIN_PATH
    env["FTRACK_CONNECT_PLUGIN_PATH"] = [
        os.path.join(
            os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-maya"
        ),
        os.path.join(
            os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-nuke"
        ),
        os.path.join(os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-rv"),
        os.path.join(
            os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect-nuke-studio"
        ),
        os.path.join(root, "environment", "FTRACK_CONNECT_PLUGIN_PATH"),
        os.path.join(os.environ["CONDA_GIT_REPOSITORY"], "ftrack-connect")
    ]

    # FTRACK_CONNECT_MAYA_PLUGINS_PATH
    env["FTRACK_CONNECT_MAYA_PLUGINS_PATH"] = [
        os.path.join(
            os.environ["CONDA_GIT_REPOSITORY"],
            "ftrack-connect-maya",
            "resource"
        )
    ]

    # FTRACK_CONNECT_NUKE_PLUGINS_PATH
    env["FTRACK_CONNECT_NUKE_PLUGINS_PATH"] = [
        os.path.join(
            os.environ["CONDA_GIT_REPOSITORY"],
            "ftrack-connect-nuke",
            "resource"
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
    env["RV_SUPPORT_PATH"] = [
        os.path.join(root, "environment", "RV_SUPPORT_PATH")
    ]

    utils.write_environment(env)


if __name__ == "__main__":
    environment_setup.build_rv_plugin()
    environment_setup.build_ftrack_connect_resources()
    main()
