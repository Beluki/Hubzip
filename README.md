
## About

Sometimes I want to mess around with some source code of a given
project in Github without cloning it, just to see the current state
or browse the files locally in my editor.

In those cases, I don't care about the logs, history, commits and
all the git stuff, therefore I just click the download button,
decompress it and start my journey. Some repositories also take
a while to clone.

Hubzip is a small Python 3 program that does the same from the
command-line by specifying the user/repository combination.

Using it is simple:

```bash
$ Hubzip.py kennethreitz/requests mitsuhiko/flask
kennethreitz/requests...
mitsuhiko/flask...

$ ls
flask-master  requests-master
```

## Command-line options

There are just two:

* `--keep` won't delete the .zip files for the repositories after
  decompressing them.

* `--quiet` supresses the `username/repository...` messages to stdout
  when downloading (useful for scripts).

## Portability

Information and error messages are written to stdout and stderr
respectively, using the current platform newline format and encoding.

The exit status is 0 on success and 1 on errors. After an error,
Hubzip will stop downloading and exit with an error message instead
of continuing with the next repository.

Note that Hubzip will overwrite any files with the same name on
the current working directory while extracting.

Hubzip is tested on Windows 7+ and on Debian (both x86 and x86-64)
using Python 3.5.0+ and requests 2.9.1+. Older versions back to Python 3.3
could work. Python 2.x is not supported.

## License

Like all my hobby projects, this is Free Software. See the [Documentation][]
folder for more information. No warranty though.

[Documentation]: Documentation

