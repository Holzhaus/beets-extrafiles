# beets-extrafiles

A plugin for [beets](http://beets.io/) that copies additional files and directories during the import process.


## Installation

**Important:** Even though beets supports Python 2, this plugin does not - it only supports Python 3.
If you really need Python 2 and you patch does not make the code considerably harder to read, feel free to file a Pull Request.

This plugin has no dependencies apart from [`setuptools`](https://pypi.org/project/setuptools/) and [`beets`](https://pypi.org/project/beets/) itself.

Since this plugin is currently not released on [PyPI](https://pypi.org/), you need to clone and install the plugin manually:

    $ git clone https://github.com/Holzhaus/beets-extrafiles.git
    $ cd beets-extrafiles
    $ ./setup.py install --user


## Usage

Activate the plugin by adding it to the `plugins` list in beet's `config.yaml`:

```yaml
plugins:
  # [...]
  - extrafiles
```

Also, you need to add [glob patterns](https://docs.python.org/3/library/glob.html#module-glob) that will be matched.
The snippet below will add a pattern group named `all` that matches all files that have an extension.

```yaml
extrafiles:
    patterns:
        all: '*.*'
```

Pattern names are useful when you want to customize the destination path that the files will be copied or moved to.
The following configuration will match all folders named `scans`, `Scans`, `artwork` or `Artwork` (using the pattern group `artworkdir`), copy them to the album path and rename them to `artwork`:

```yaml
extrafiles:
    patterns:
        artworkdir:
          - '[sS]cans/'
          - '[aA]rtwork/'
    paths:
        artworkdir: $albumpath/artwork
```


## Development

After cloning the git repository, you can use `setup.py` to set up the necessary symlinks for you:

    $ git clone https://github.com/Holzhaus/beets-extrafiles.git
    $ cd beets-extrafiles
    $ ./setup.py develop --user

When adding changes, please conform to [PEP 8](https://www.python.org/dev/peps/pep-0008/).
Also, please add docstrings to all modules, functions and methods that you create.
Use can check this by running [`flake8`](http://flake8.pycqa.org/en/latest/index.html) with the [`flake8-docstrings` plugin](https://pypi.org/project/flake8-docstrings/).

Using [pre-commit](https://pre-commit.com/) will perform these checks automatically when committing changes.
You can install the pre-commit hooks by executing this in the git repository's root directory:

    $ pre-commit install

You should also *test every single commit* by running unittests, i.e.:

    $ ./setup.py test

If a test fails, please fix it *before* you create a pull request.
If you accidently commit something that still contains errors, please amend, squash or fixup that commit instead of adding a new one.
