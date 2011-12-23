# coded4

Ever wondered how much time have you spent on a project?...

_coded4_ ('coded for ...') calculates approximate time that one has spent coding
particular project. It uses commit timestamps to reconstruct coding sessions
for every commiter in given Git or Hg repository.

## Usage

...is simple:

    $ ./coded4.py <directory>

For example, you can find out how much time was spent on this very project:

    $ git clone git://github.com/Xion/coded4.git
    $ cd coded4
    $ ./coded4.py .

This should print something like that:

    name             commits time    
    ---------------------------------
    Karol Kuczmarski 21      02:16:19

As you can see, _coded4_ didn't take all that long to make ;)

For more options:

    $ ./coded4.py --help

---

This tiny project is licensed under MIT.