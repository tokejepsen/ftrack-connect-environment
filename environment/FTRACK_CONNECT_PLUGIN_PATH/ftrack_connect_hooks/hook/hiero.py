import os
import re
import getpass
import sys
import pprint
import logging

import ftrack
import ftrack_connect.application


class LaunchAction(object):
    """ftrack connect legacy plugins discover and launch action."""

    identifier = "hiero"

    def __init__(self, applicationStore, launcher):
        """Initialise action with *applicationStore* and *launcher*.

        *applicationStore* should be an instance of
        :class:`ftrack_connect.application.ApplicationStore`.

        *launcher* should be an instance of
        :class:`ftrack_connect.application.ApplicationLauncher`.

        """
        super(LaunchAction, self).__init__()

        self.logger = logging.getLogger(
            __name__ + "." + self.__class__.__name__
        )

        self.applicationStore = applicationStore
        self.launcher = launcher

    def register(self):
        """Override register to filter discover actions on logged in user."""
        ftrack.EVENT_HUB.subscribe(
            "topic=ftrack.action.discover and source.user.username={0}".format(
                getpass.getuser()
            ),
            self.discover
        )

        ftrack.EVENT_HUB.subscribe(
            "topic=ftrack.action.launch and source.user.username={0} "
            "and data.actionIdentifier={1}".format(
                getpass.getuser(), self.identifier
            ),
            self.launch
        )

    def discover(self, event):
        """Return discovered applications."""

        items = []
        applications = self.applicationStore.applications
        applications = sorted(
            applications, key=lambda application: application["label"]
        )

        for application in applications:
            applicationIdentifier = application["identifier"]
            label = application["label"]
            items.append({
                "actionIdentifier": self.identifier,
                "label": label,
                "variant": application.get("variant", None),
                "description": application.get("description", None),
                "icon": application.get("icon", "default"),
                "applicationIdentifier": applicationIdentifier
            })

        return {
            "items": items
        }

    def launch(self, event):
        """Handle *event*.

        event["data"] should contain:

            *applicationIdentifier* to identify which application to start.

        """
        # Prevent further processing by other listeners.
        event.stop()
        applicationIdentifier = (
            event["data"]["applicationIdentifier"]
        )

        context = event["data"].copy()
        context["source"] = event["source"]

        applicationIdentifier = event["data"]["applicationIdentifier"]
        context = event["data"].copy()
        context["source"] = event["source"]

        return self.launcher.launch(
            applicationIdentifier, context
        )


class ApplicationStore(ftrack_connect.application.ApplicationStore):
    """Discover and store available applications on this host."""

    def _discoverApplications(self):
        """Return a list of applications that can be launched from this host.

        An application should be of the form:

            dict(
                "identifier": "name_version",
                "label": "Name",
                "variant": "version",
                "description": "description",
                "path": "Absolute path to the file",
                "version": "Version of the application",
                "icon": "URL or name of predefined icon"
            )

        """
        applications = []

        if sys.platform == "darwin":
            prefix = ["/", "Applications"]

            applications.extend(self._searchFilesystem(
                versionExpression=r"Hiero(?P<version>.*)\/.+$",
                expression=prefix + ["Hiero\d.+", "Hiero\d.+.app"],
                label="Hiero",
                variant="{version}",
                applicationIdentifier="hiero_{version}",
                icon="hiero"
            ))

            applications.extend(self._searchFilesystem(
                versionExpression=r"Nuke(?P<version>.*)\/.+$",
                expression=prefix + ["Nuke.*", "Hiero\d[\w.]+.app"],
                label="Hiero",
                variant="{version}",
                applicationIdentifier="hiero_{version}",
                icon="hiero"
            ))

        elif sys.platform == "win32":
            prefix = ["C:\\", "Program Files.*"]

            applications.extend(self._searchFilesystem(
                expression=prefix + ["Hiero\d.+", "hiero.exe"],
                label="Hiero",
                variant="{version}",
                applicationIdentifier="hiero_{version}",
                icon="hiero"
            ))

            # Somewhere along the way The Foundry changed the default install
            # directory.
            # Add the old directory as expression to find old installations of
            # Hiero as well.
            applications.extend(self._searchFilesystem(
                expression=prefix + ["The Foundry", "Hiero\d.+", "hiero.exe"],
                label="Hiero",
                variant="{version}",
                applicationIdentifier="hiero_{version}",
                icon="hiero"
            ))

            version_expression = re.compile(
                r"Nuke(?P<version>[\d.]+[\w\d.]*)"
            )

            applications.extend(self._searchFilesystem(
                expression=prefix + ["Nuke.*", "Nuke\d.+.exe"],
                versionExpression=version_expression,
                label="Hiero",
                variant="{version}",
                applicationIdentifier="hiero_{version}",
                icon="hiero",
                launchArguments=["--hiero"]
            ))

        elif sys.platform == "linux2":
            applications.extend(self._searchFilesystem(
                versionExpression=r"Hiero(?P<version>.*)\/.+\/.+$",
                expression=[
                    "/", "usr", "local", "Hiero.*", "bin", "Hiero\d.+"
                ],
                label="Hiero",
                variant="{version}",
                applicationIdentifier="hiero_{version}",
                icon="hiero"
            ))

            applications.extend(self._searchFilesystem(
                expression=["/", "usr", "local", "Nuke.*", "Nuke\d.+"],
                label="Hiero",
                variant="{version}",
                applicationIdentifier="hiero_{version}",
                icon="hiero",
                launchArguments=["--hiero"]
            ))

        self.logger.debug(
            "Discovered applications:\n{0}".format(
                pprint.pformat(applications)
            )
        )

        return applications


class ApplicationLauncher(ftrack_connect.application.ApplicationLauncher):
    """Custom launcher to modify environment before launch."""

    def __init__(self, application_store):
        super(ApplicationLauncher, self).__init__(application_store)

    def _getApplicationEnvironment(self, application, context=None):
        """Modify and return environment with legacy plugins added."""
        # Make sure to call super to retrieve original environment
        # which contains the selection and ftrack API.
        environment = super(
            ApplicationLauncher, self
        )._getApplicationEnvironment(application, context)

        legacyPluginsPath = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "resource", "legacy_plugins"
            )
        )
        """
        # Append legacy plugin base to PYTHONPATH.
        environment = ftrack_connect.application.appendPath(
            legacyPluginsPath, "PYTHONPATH", environment
        )

        # Load Hiero plugins if application is Hiero.
        hieroPluginPath = os.path.join(
            legacyPluginsPath, "ftrackHieroPlugin"
        )

        environment = ftrack_connect.application.appendPath(
            hieroPluginPath, "HIERO_PLUGIN_PATH", environment
        )

        # Add the foundry asset manager packages if application is
        # Nuke, NukeStudio or Hiero.
        foundryAssetManagerPluginPath = os.path.join(
            legacyPluginsPath, "ftrackProvider"
        )

        environment = ftrack_connect.application.appendPath(
            foundryAssetManagerPluginPath,
            "FOUNDRY_ASSET_PLUGIN_PATH",
            environment
        )

        foundryAssetManagerPath = os.path.join(
            legacyPluginsPath,
            "theFoundry"
        )

        environment = ftrack_connect.application.prependPath(
            foundryAssetManagerPath, "PYTHONPATH", environment
        )
        """
        return environment


def register(registry, **kw):
    """Register hooks for ftrack connect legacy plugins."""

    # Validate that registry is the correct ftrack.Registry. If not,
    # assume that register is being called with another purpose or from a
    # new or incompatible API and return without doing anything.
    if registry is not ftrack.EVENT_HANDLERS:
        # Exit to avoid registering this plugin again.
        return

    # Create store containing applications.
    applicationStore = ApplicationStore()

    # Create a launcher with the store containing applications.
    launcher = ApplicationLauncher(applicationStore)

    # Create action and register to respond to discover and launch actions.
    action = LaunchAction(applicationStore, launcher)
    action.register()
