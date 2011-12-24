# coded4

Ever wondered how much time have you spent on a project?...

_coded4_ ('coded for ...') calculates approximate time that one has spent coding
particular project. It uses commit timestamps to reconstruct coding sessions
for every commiter in given Git or Hg repository.

## Installation

A standard `setup.py` is provided:

    $ git clone git://github.com/Xion/coded4.git
    $ cd coded4
    $ ./setup.py develop

Use `develop` instead of `install` so you can easily `git pull` any updates.

## Usage

...is simple:

    $ coded4 <directory-with-repo>

For example, if you have just installed _coded4_ and are still inside its directory, type:

    $ coded4 .

This should print something like that:

    name             commits time    
    ---------------------------------
    Karol Kuczmarski 21      02:16:19

As you can see, _coded4_ didn't take all that long to make ;)

For more options:

    $ coded4 --help

---

This small project is licensed under MIT.