# -*- coding: utf-8 -*-
"""Tests for the beets-extrafiles plugin."""
import os
import shutil
import tempfile
import unittest.mock

import beets.util.confit

import beetsplug.extrafiles

RSRC = os.path.join(os.path.dirname(__file__), 'rsrc')


class BaseTestCase(unittest.TestCase):
    """Base testcase class that sets up example files."""

    PLUGIN_CONFIG = {
        'extrafiles': {
            'patterns': {
                'log': ['*.log'],
                'cue': ['*.cue'],
                'artwork': ['scans/', 'Scans/', 'artwork/', 'Artwork/'],
            },
            'paths': {
                'artwork': '$albumpath/artwork',
                'log': '$albumpath/audio',
            },
        },
    }

    def setUp(self):
        """Set up example files and instanciate the plugin."""
        self.srcdir = tempfile.TemporaryDirectory(suffix='src')
        self.dstdir = tempfile.TemporaryDirectory(suffix='dst')
        for filename in ('file.cue', 'file.txt', 'file.log'):
            open(os.path.join(self.srcdir.name, filename), mode='w').close()

        shutil.copy(
            os.path.join(RSRC, 'full.mp3'),
            os.path.join(self.srcdir.name, 'file.mp3'),
        )

        config = beets.util.confit.RootView(sources=[
            beets.util.confit.ConfigSource.of(self.PLUGIN_CONFIG),
        ])

        artwork_path = os.path.join(self.srcdir.name, 'scans')
        os.mkdir(artwork_path)
        for filename in ('front.jpg', 'back.jpg'):
            open(os.path.join(artwork_path, filename), mode='w').close()

        with unittest.mock.patch(
                'beetsplug.extrafiles.beets.plugins.beets.config', config,
        ):
            self.plugin = beetsplug.extrafiles.ExtraFilesPlugin('extrafiles')

    def tearDown(self):
        """Remove the example files."""
        self.srcdir.cleanup()
        self.dstdir.cleanup()
