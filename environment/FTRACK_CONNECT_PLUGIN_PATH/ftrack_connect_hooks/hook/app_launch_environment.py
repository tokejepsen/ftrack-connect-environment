import os
import logging
import subprocess

import ftrack
import ftrack_connect_rv

logging.basicConfig()
logger = logging.getLogger()


def modify_application_launch(event):
    """Modify the application environment."""

    data = event["data"]

    # Prepending maya python modules to force PySide to load correctly
    if event["data"]["application"]["identifier"].startswith("maya"):
        path = event["data"]["application"]["path"]
        site_packages = os.path.join(os.path.dirname(os.path.dirname(path)),
                                     "Python", "Lib", "site-packages")

        data["options"]["env"]["PYTHONPATH"] = (
            site_packages + os.pathsep + data["options"]["env"]["PYTHONPATH"]
        )

    # Installing RV plugin
    # Currently Windows only
    if event["data"]["application"]["identifier"].startswith("rv"):
        path = event["data"]["application"]["path"]
        rvpkg = os.path.join(os.path.dirname(path), "rvpkg.exe")

        rvpkg_version = '.'.join(ftrack_connect_rv.__version__.split('.'))
        plugin_file = 'ftrack-{0}.rvpkg'.format(rvpkg_version)
        package = os.path.join(
            os.path.join(
                os.environ["CONDA_GIT_REPOSITORY"],
                "ftrack-connect-environment"
            ),
            "environment",
            "RV_SUPPORT_PATH",
            "Packages",
            plugin_file
        )

        subprocess.call([rvpkg, "-install", package])

    return data


def register(registry, **kw):
    """Register location plugin."""

    # Validate that registry is the correct ftrack.Registry. If not,
    # assume that register is being called with another purpose or from a
    # new or incompatible API and return without doing anything.
    if registry is not ftrack.EVENT_HANDLERS:
        # Exit to avoid registering this plugin again.
        return

    ftrack.EVENT_HUB.subscribe(
        "topic=ftrack.connect.application.launch",
        modify_application_launch
    )

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)

    ftrack.setup()

    ftrack.EVENT_HUB.subscribe(
        "topic=ftrack.connect.application.launch",
        modify_application_launch)
    ftrack.EVENT_HUB.wait()
