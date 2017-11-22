import os
import logging
import subprocess

import ftrack

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

    # Invalidate PySide importing in 2017+ to ensure PySide2 is loaded in
    # favour of PySide. This is done through a custom userSetup.py.
    # Plugins like Xgen wrongly tries to import PySide before trying PySide2.
    if int(event["data"]["application"]["version"]) > 2016:
        data["options"]["env"]["PYTHONPATH"] += (
            os.pathsep + os.path.abspath(
                os.path.join(__file__, "..", "..", "invalidate_pyside")
            )
        )

    # Installing RV plugin
    # Currently Windows only
    if event["data"]["application"]["identifier"].startswith("rv"):
        path = event["data"]["application"]["path"]
        rvpkg = os.path.join(os.path.dirname(path), "rvpkg.exe")

        # Check if ftrack plugin is available and installed
        for line in subprocess.check_output([rvpkg, "-list"]).split("\n"):
            if "\"ftrack\"" in line:
                if not line.startswith("I"):
                    # Install ftrack plugin
                    subprocess.call([rvpkg, "-install", "ftrack"])

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
