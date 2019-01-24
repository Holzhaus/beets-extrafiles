# -*- coding: utf-8 -*-
"""beets-extrafiles plugin for beets."""
import beets.plugins


class ExtraFilesPlugin(beets.plugins.BeetsPlugin):
    """Plugin main class."""

    def __init__(self, *args, **kwargs):
        """Initialize a new plugin instance."""
        super(ExtraFilesPlugin, self).__init__(*args, **kwargs)

        self.register_listener('item_moved', self.on_item_moved)
        self.register_listener('item_copied', self.on_item_copied)
        self.register_listener('cli_exit', self.on_cli_exit)

    def on_item_moved(self, item, source, destination):
        """Run this listener function on item_moved events."""

    def on_item_copied(self, item, source, destination):
        """Run this listener function on item_copied events."""

    def on_cli_exit(self, lib):
        """Run this listener function when the CLI exits."""
