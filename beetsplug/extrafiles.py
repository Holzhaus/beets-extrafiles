# -*- coding: utf-8 -*-
"""beets-extrafiles plugin for beets."""
import glob
import os
import shutil
import traceback

import beets.dbcore.db
import beets.library
import beets.mediafile
import beets.plugins
import beets.ui
import beets.util.functemplate


class FormattedExtraFileMapping(beets.dbcore.db.FormattedMapping):
    """Formatted Mapping that allows path separators for certain keys."""

    def __getitem__(self, key):
        """Get the formatted version of model[key] as string."""
        if key == 'albumpath':
            value = self.model._type(key).format(self.model.get(key))
            if isinstance(value, bytes):
                value = value.decode('utf-8', 'ignore')
            return value
        else:
            return super(FormattedExtraFileMapping, self).__getitem__(key)


class ExtraFileModel(beets.dbcore.db.Model):
    """Model for a  FormattedExtraFileMapping instance."""

    _fields = {
        'artist':      beets.dbcore.types.STRING,
        'albumartist': beets.dbcore.types.STRING,
        'album':       beets.dbcore.types.STRING,
        'albumpath':   beets.dbcore.types.STRING,
        'filename':    beets.dbcore.types.STRING,
    }

    @classmethod
    def _getters(cls):
        """Return a mapping from field names to getter functions."""
        return {}


class ExtraFilesPlugin(beets.plugins.BeetsPlugin):
    """Plugin main class."""

    def __init__(self, *args, **kwargs):
        """Initialize a new plugin instance."""
        super(ExtraFilesPlugin, self).__init__(*args, **kwargs)

        self._move_files = set()
        self._copy_files = set()
        self._scanned_paths = set()
        self.path_formats = beets.ui.get_path_formats(self.config['paths'])

        self.register_listener('item_moved', self.on_item_moved)
        self.register_listener('item_copied', self.on_item_copied)
        self.register_listener('cli_exit', self.on_cli_exit)

    def on_item_moved(self, item, source, destination):
        """Run this listener function on item_moved events."""
        self._move_files.update(
            set(self.gather_tasks(item, source, destination)),
        )

    def on_item_copied(self, item, source, destination):
        """Run this listener function on item_copied events."""
        self._copy_files.update(
            set(self.gather_tasks(item, source, destination)),
        )

    def on_cli_exit(self, lib):
        """Run this listener function when the CLI exits."""
        self.process_files(self._copy_files, action=self._copy_file)
        self.process_files(self._move_files, action=self._move_file)

    def _copy_file(self, path, dest):
        """Copy path to dest."""
        self._log.info('Copying extra file: {0} -> {0}', path, dest)
        if os.path.isdir(path):
            if os.path.exists(dest):
                raise beets.util.FilesystemError(
                    'file exists', 'copy',
                    (path, dest),
                )

            try:
                shutil.copytree(path, dest)
            except (OSError, IOError) as exc:
                raise beets.util.FilesystemError(
                    exc, 'copy', (path, dest),
                    traceback.format_exc(),
                )
        else:
            beets.util.copy(path, dest)

    def _move_file(self, path, dest):
        """Move path to dest."""
        self._log.info('Moving extra file: {0} -> {0}', path, dest)
        shutil.move(path, dest)

    def process_files(self, files, action):
        """Move path to dest."""
        # Skip files that were moved by other plugins
        skipped_files = set()
        for source, destination in files:
            if not os.path.exists(source):
                self._log.warning('Skipping missing source file: {0}', source)
                skipped_files.add(source)

            if os.path.exists(destination):
                self._log.warning(
                    'Skipping already present destination file: {0}',
                    destination,
                )
                skipped_files.add(source)

            destpath = beets.util.bytestring_path(destination)
            destpath = beets.util.unique_path(destpath)
            beets.util.mkdirall(destpath)

            try:
                action(source, destination)
            except beets.util.FilesystemError:
                self._log.warning(
                    'Failed to process file: {} -> {}', source,
                    destination,
                )

    def gather_tasks(self, item, source, destination):
        """Generate a sequence of (path, destpath) tuples for an item."""
        meta = {
            'artist': item.artist or u'None',
            'albumartist': item.albumartist or u'None',
            'album': item.album or u'None',
            'albumpath': beets.util.displayable_path(
                os.path.dirname(destination),
            ),
        }

        for path, category in self.find_files(
            source,
            skip=self._scanned_paths,
        ):
            destpath = self.get_destination(path, category, meta.copy())
            yield path, destpath

    def find_files(self, source, skip=set()):
        """Find all files matched by the patterns."""
        source_path = beets.util.displayable_path(os.path.dirname(source))

        if source_path in skip:
            return

        for category, patterns in self.config['patterns'].get(dict).items():
            for pattern in patterns:
                globpath = os.path.join(glob.escape(source_path), pattern)
                for path in glob.iglob(globpath):
                    ext = os.path.splitext(path)[1]
                    if len(ext) > 1 and ext[1:] in beets.mediafile.TYPES:
                        continue

                    yield (path, category)

        skip.add(source_path)

    def get_destination(self, path, category, meta):
        """Get the destination path for a source file."""
        old_filename, fileext = os.path.splitext(os.path.basename(path))

        mapping = FormattedExtraFileMapping(
            ExtraFileModel(
                filename=beets.util.displayable_path(old_filename),
                **meta
            ), for_path=True,
        )

        for query, path_format in self.path_formats:
            if query == category:
                break
        else:
            # No query matched; use original filename
            path_format = beets.util.functemplate.Template(
                '$albumpath/$filename',
            )

        # Get template funcs and evaluate against mapping
        funcs = beets.library.DefaultTemplateFunctions().functions()
        filepath = path_format.substitute(mapping, funcs) + fileext

        # Sanitize filename
        filename = beets.util.sanitize_path(os.path.basename(filepath))
        dirname = os.path.dirname(filepath)
        filepath = os.path.join(dirname, filename)

        return filepath
