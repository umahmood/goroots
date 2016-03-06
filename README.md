# Goroots

Goroots is a Python 3 tool, which helps manage multiple versions/installations of 
[Go](https://golang.org) on a machine. If you want to run multiples versions of Go 
on your development box in a painless manner, then use Goroots. 

[![asciicast](https://asciinema.org/a/38483.png)](https://asciinema.org/a/38483)

# Installation

**Note**: Goroots is only avaiable on [Linux and OSX](#testing), and for developers using the Bash shell.<br/>
**Note**: Goroots installs all Go downloads to */opt/groot*. You will need create this directory and make it writable for the current user.

    $ git clone https://github.com/umahmood/goroots.git && cd goroots
    $ pip install -r requirements.txt
    $ sudo mkdir /opt/goroots
    $ sudo chown <uid> /opt/goroots e.g. sudo chown johndoe /opt/goroots

# Usage

List Go downloads valid to install on this machine:

    $ goroots.py --list

    Go downloads matching your architecture: linux-amd64

    File Name                      Kind       OS         Arch      Size   SHA1/256 Checksum
    go1.6.linux-amd64.tar.gz       Archive    Linux      64-bit    81MB   5470eac...2e80b
    go1.5.3.linux-amd64.tar.gz     Archive    Linux      64-bit    76MB   43afe0c...0ae53
    go1.5.2.linux-amd64.tar.gz     Archive    Linux      64-bit    73MB   cae87ed...1234e
    go1.5.1.linux-amd64.tar.gz     Archive    Linux      64-bit    74MB   46eecd2...75fe0
    go1.5.linux-amd64.tar.gz       Archive    Linux      64-bit    74MB   5817fa4...f3bd5
    go1.4.3.linux-amd64.tar.gz     Archive    Linux      64-bit    58MB   332b642...507fe
    go1.4.2.linux-amd64.tar.gz     Archive    Linux      64-bit           5020af9...b0aff
    go1.4.1.linux-amd64.tar.gz     Archive    Linux      64-bit           3e87120...c51ed
    go1.4.linux-amd64.tar.gz       Archive    Linux      64-bit           cd82abc...ac4c6
    go1.3.3.linux-amd64.tar.gz     Archive    Linux      64-bit           14068fb...24646
    go1.3.2.linux-amd64.tar.gz     Archive    Linux      64-bit           0e4b612...cbe42
    go1.3.1.linux-amd64.tar.gz     Archive    Linux      64-bit           3af011c...97143
    go1.3.linux-amd64.tar.gz       Archive    Linux      64-bit           b6b1549...06ba6
    go1.2.2.linux-amd64.tar.gz     Archive    Linux      64-bit           6bd151c...8ebb5

Show a list of downloaded Go versions:

    $ goroots.py --show
    Installed go versions in /opt/goroots:
    - 1.5.3
    - 1.5
    - 1.4.2

Get a specific version of Go:

    $ goroots.py --get 1.5.2


Set and use a specific version of go:

    $ goroots.py --set 1.5.2

Remove a specific version of Go:

    $ goroots.py --rem 1.5.2 

Display program help:

    $ goroots.py --help
        
    usage: goroots.py [--help] [--version] [--list] [--show] [--get GET]
                      [--rem REM]

    goroots helps manage multiple versions/installations of golang on a machine.

    optional arguments:
      --help     Show this message and exit.
      --version  Show program version and exit.
      --list     Display a list of available go downloads.
      --show     Show all the go versions downloaded.
      --get GET  Download and install a version of go.
      --set SET  Set and use this version of go.
      --rem REM  Remove this downloaded version of go.

    examples:

    list go downloads valid to install on this machine:

        $ goroots.py --list

    show a list of downloaded go versions:

        $ goroots.py --show

    get a specific version of go:

        $ goroots.py --get 1.5.2

    set and use a specific version of go:

        $ goroots.py --set 1.5.2

    remove a specific version of go:

        $ goroots.py --rem 1.5.2

# Dependencies

- Python 3 
- [beautifulsoup4 (4.4.1)](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [requests (2.9.1)](http://docs.python-requests.org/en/master/)

# Testing

Goroots has been tested on:

- Fedora Linux 20 64 bit
- OS X 10.11 64 bit

# License

See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).
