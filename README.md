# beets-extrafiles

A plugin for [beets](http://beets.io/) that copies additional files and directories during the import process.


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
