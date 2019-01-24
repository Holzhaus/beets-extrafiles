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


class FindPathsTestCase(BaseTestCase):
    """Testcase that checks if all extra files are found."""

    def testFindPaths(self):
        """Test if extra files are found in the media file's directory."""
        files = set(self.plugin.find_files(
            source=os.path.join(self.srcdir.name, 'file.mp3'),
        ))

        expected_files = set([
            (os.path.join(self.srcdir.name, 'scans/'), 'artwork'),
            (os.path.join(self.srcdir.name, 'file.cue'), 'cue'),
            (os.path.join(self.srcdir.name, 'file.log'), 'log'),
        ])

        assert files == expected_files


class MoveFilesTestCase(BaseTestCase):
    """Testcase that moves files."""

    def testMoveFiles(self):
        """Test if extra files are detected an moved correctly."""
        source = os.path.join(self.srcdir.name, 'file.mp3')
        destination = os.path.join(self.dstdir.name, 'moved_file.mp3')

        item = beets.library.Item.from_path(source)
        shutil.move(source, destination)

        self.plugin.on_item_moved(
            item, beets.util.bytestring_path(source),
            beets.util.bytestring_path(destination),
        )
        self.plugin.on_cli_exit(None)

        # Check source directory
        assert os.path.exists(os.path.join(self.srcdir.name, 'file.txt'))
        assert not os.path.exists(os.path.join(self.srcdir.name, 'file.cue'))
        assert not os.path.exists(os.path.join(self.srcdir.name, 'file.log'))
        assert not os.path.exists(os.path.join(self.srcdir.name, 'audio.log'))

        assert not os.path.exists(os.path.join(self.srcdir.name, 'artwork'))
        assert not os.path.exists(os.path.join(self.srcdir.name, 'scans'))

        # Check destination directory
        assert not os.path.exists(os.path.join(self.dstdir.name, 'file.txt'))
        assert os.path.exists(os.path.join(self.dstdir.name, 'file.cue'))
        assert not os.path.exists(os.path.join(self.dstdir.name, 'file.log'))
        assert os.path.exists(os.path.join(self.dstdir.name, 'audio.log'))

        assert not os.path.isdir(os.path.join(self.dstdir.name, 'scans'))
        assert os.path.isdir(os.path.join(self.dstdir.name, 'artwork'))
        assert (set(os.listdir(os.path.join(self.dstdir.name, 'artwork'))) ==
                set(('front.jpg', 'back.jpg')))


class CopyFilesTestCase(BaseTestCase):
    """Testcase that copies files."""

    def testCopyFiles(self):
        """Test if files are detected and copied correctly."""
        source = os.path.join(self.srcdir.name, 'file.mp3')
        destination = os.path.join(self.dstdir.name, 'moved_file.mp3')

        item = beets.library.Item.from_path(source)
        shutil.copy(source, destination)

        self.plugin.on_item_copied(
            item, beets.util.bytestring_path(source),
            beets.util.bytestring_path(destination),
        )
        self.plugin.on_cli_exit(None)

        # Check source directory
        assert os.path.exists(os.path.join(self.srcdir.name, 'file.txt'))
        assert os.path.exists(os.path.join(self.srcdir.name, 'file.cue'))
        assert os.path.exists(os.path.join(self.srcdir.name, 'file.log'))
        assert not os.path.exists(os.path.join(self.srcdir.name, 'audio.log'))

        assert not os.path.exists(os.path.join(self.srcdir.name, 'artwork'))
        assert os.path.isdir(os.path.join(self.srcdir.name, 'scans'))
        assert (set(os.listdir(os.path.join(self.srcdir.name, 'scans'))) ==
                set(('front.jpg', 'back.jpg')))

        # Check destination directory
        assert not os.path.exists(os.path.join(self.dstdir.name, 'file.txt'))
        assert os.path.exists(os.path.join(self.dstdir.name, 'file.cue'))
        assert not os.path.exists(os.path.join(self.dstdir.name, 'file.log'))
        assert os.path.exists(os.path.join(self.dstdir.name, 'audio.log'))

        assert not os.path.exists(os.path.join(self.dstdir.name, 'scans'))
        assert os.path.isdir(os.path.join(self.dstdir.name, 'artwork'))
        assert (set(os.listdir(os.path.join(self.dstdir.name, 'artwork'))) ==
                set(('front.jpg', 'back.jpg')))
