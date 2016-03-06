#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import pwd
import os
import tarfile
import argparse
import hashlib
import platform
import shutil
import subprocess

import requests
from bs4 import BeautifulSoup as bs

__author__ = "Usman Mahmood"
__license__ = "MIT License"
__version__ = "1.0.0"

USER         = pwd.getpwuid( os.getuid() ).pw_name
INSTALL_BASE = '/opt/goroots'

def get_golang_dls():
    """
    Scrapes https://golang.org/dl/ and returns a tuple containing a list and 
    dictionary of available go downloads.

    @return: tuple(list, dict)  - n versions from golang.org/dl   
    """    
    try:
        URI      = 'https://golang.org/dl/'
        response = requests.get(URI)
        if response.status_code is not requests.codes.ok:
            print("error making http request", response.status_code)
            sys.exit(1)
        soup   = bs(response.text, 'html.parser')
        tables = soup.findAll('table')
    except (AttributeError, requests.ConnectionError, requests.Timeout) as e:
        print(*e.args)
        sys.exit(1)

    go_downloads_d  = dict()
    go_downloads_l  = list()
    download_number = 0

    for table in tables:
        for row in table.findAll('tr'):
            try:
                items = []
                for col in row.findAll('td'):
                    h = col.get('class')
                    if isinstance(h, list) and len(h) > 0:
                        if h[0] == 'filename':
                            download_url = col.find('a').get('href')
                            n = download_url.rfind('/') 
                            download_number += 1
                            items.append(download_number)
                            items.append(download_url[n+1:])
                            go_downloads_d[download_number] = {'url': download_url}
                    else:
                        items.append(col.text.strip())
                    if len(items) % 7 == 0:
                        num      = items[0]
                        filename = items[1]
                        kind     = items[2] 
                        os       = items[3] 
                        arch     = items[4] 
                        size     = items[5]
                        checksum = items[6]
                        
                        go_downloads_d[download_number].update({
                            'filename':filename, 'kind':kind, 'os':os, 
                            'arch':arch, 'size':size, 'checksum':checksum
                        })

                        go_downloads_l.append(items)
            except AttributeError as e:
                print(*e.args)
                sys.exit(1)

    return (go_downloads_l, go_downloads_d)

def download_file(path_to_download, url):
    """
    Given a valid URL downloads it.

    @param: path_to_download (string) - the path to download the tar file to. 
    @param: url (string)              - the url to get.

    @return: (string) - path to the downloaded file.
    """
    location = url.rfind('/')
    if location is not -1:
        local_filename = url[location+1:]
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code is not requests.codes.ok:
            print('error downloading file - http', response.status_code)
    except requests.ConnectionError as e:
        print(*e.args)
        sys.exit(1)

    file_path = path_to_download + os.sep + local_filename
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    return file_path

def get_arch():
    """
    Returns the architecture of this machine in the same format it appears in go 
    download file names.
    """
    bits = platform.architecture()[0][:2]
    if bits == '64':
        proc = 'amd64'
    elif bits == '32':
        proc = '386'

    if sys.platform.startswith('linux'):
        os = 'linux'
    elif sys.platform.startswith('darwin'):
        os = 'darwin'
    
    return os + '-' + proc

def install_base_error():
    """
    Print error message when install directory does not exist.
    """
    print("install path", INSTALL_BASE, "does not exist, please create it with:")
    print('1. sudo mkdir', INSTALL_BASE)
    print('2. sudo chown', USER, INSTALL_BASE)
    sys.exit(1)

def get_installed_versions():
    """
    Returns a list of go installations in the install base.
    """
    try:
        return os.listdir(INSTALL_BASE)
    except FileNotFoundError as e:
        install_base_error()

def run(goroot):
    """
    Run a bash shell pointing to the specified GOROOT. Run ends the current
    process when the bash shell exits.

    @param: goroot (string) - The path to the target GOROOT.
    """
    path = os.environ["PATH"]
    
    os.environ["GOROOT"] = goroot
    os.environ["PATH"]   = goroot + os.sep + 'bin:' + path 

    print('GOROOT set to', goroot)
    os.system('go version')
    print("to go back to default go installation, type 'exit'")
    ret = subprocess.call(['bash'])
    sys.exit(ret)

################################################################################

def list_go_versions(): # --list
    """
    Displays a table of available go downloads for this machine.
    """
    rowfmt = '{filename:40} {kind:10} {os:12} {arch:10} {size:7} {checksum}'
    head   = rowfmt.format(n='#', filename='File Name', kind='Kind', os='OS',
                        arch='Arch', size='Size', checksum='SHA1/256 Checksum')

    machine_arch = get_arch()
    items  = get_golang_dls()[0]
    if items:
        print('Go downloads matching your architecture:', machine_arch, '\n')
        print(head)

    for row in items:
        filename = row[1]
        
        if not (machine_arch in filename and filename.endswith('tar.gz')):
            continue

        kind     = row[2]
        os       = row[3]
        arch     = row[4]
        size     = row[5]
        checksum = row[6]
        
        o = rowfmt.format(filename=filename, kind=kind, os=os, arch=arch, 
            size=size, checksum=checksum)

        print(o)

    if items: print('\n')

def get_go_version(version): # --get
    """
    Finds, verifies and installs a version of go to the install base. 

    @param: version (string) - the version number to remove e.g. 1.5.3
    """
    if not os.path.exists(INSTALL_BASE):
        install_base_error()
        sys.exit(1)
    elif not os.access(INSTALL_BASE, os.W_OK):
        e = 'Permission denied: {0} is not writable. Directory needs \
        \nto be owned by {1}, try running: sudo chown {2} {3}'
        print(e.format(INSTALL_BASE, USER, USER, INSTALL_BASE))
        sys.exit(1)

    # is the user trying to get a version already installed?
    if version in get_installed_versions():
        print(version, 'already installed.')
        print('use --set', version, 'to use this version')
        return 

    arch = get_arch()
    print('Architecture is', arch)

    dl_data = get_golang_dls()[1]

    target = dict()
    for _, d in dl_data.items():
        fn = d['filename']
        if version in fn and arch in fn and fn.endswith('tar.gz'):
            target = d
            break

    if not target:
        print('Go version', version, 'not found.')
        print('Use option --list flag to select a version.')
        return

    print('Installing', target['filename'], '...')
    file_path = download_file(INSTALL_BASE, target['url'])

    print('Validating checksum...')
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        sha256.update(f.read())

    if sha256.hexdigest() == target['checksum']:
        print('File passed SHA256 checksum test.')
    else:
        print('File failed SHA256 checksum test, trying SHA1 checksum...')        
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            sha1.update(f.read())
        if sha1.hexdigest() == target['checksum']:
            print('File passed SHA1 checksum test.')
        else:
            print('File failed SHA1 checksum test, exiting...')
            sys.exit(1)        

    print('Extracting', file_path, '...')
    with tarfile.open(file_path, 'r') as tar:
        tar.extractall(path=INSTALL_BASE + os.sep + version)
        os.unlink(file_path)

    print("Done.")

def set_go_version(version): # --set
    """
    Set and use a specific version of go.

    @param: version (string) - the version number to set e.g. 1.5.3
    """
    if version not in get_installed_versions():
        print(version, 'not installed.')
        print('use --get', version, 'to install this version')
        return 
    goroot = INSTALL_BASE + os.sep + version + os.sep + 'go'
    run(goroot)

def show_installed_versions(): # --show
    """
    List all the downloaded go versions in the install base.
    """
    installed = get_installed_versions()
    if not installed:
        print("There are no installed go versions. See option --get")
    else:
        print('Installed go versions in', INSTALL_BASE + ':')
        for i in installed:
            print('-', i)

def remove_installed_version(version): # --rem
    """
    Removes a versions of go from the install base.

    @param: version (string) - the version number to remove e.g. 1.5.3
    """
    try:
        target = INSTALL_BASE + os.sep + version
        shutil.rmtree(target)    
    except FileNotFoundError as e:
        if os.path.exists(INSTALL_BASE):
            print('Go version', version, 'does not exist.')
            show_installed_versions()
        else:
            install_base_error()

def main():
    parser = argparse.ArgumentParser(prog='goroots.py', add_help=False, 
                        description="goroots helps manage multiple \
                        versions/installations of golang on a machine.")

    parser.add_argument('--help', action='store_true',
                        help='Show this message and exit.')

    parser.add_argument('--version', action='store_true',
                        help='Show program version and exit.')

    parser.add_argument('--list', action='store_true',
                        help='Display a list of available go downloads.')

    parser.add_argument('--show', action='store_true',
                        help='Show all the go versions downloaded.')

    parser.add_argument('--get', default='', type=str,
                        help='Download and install a version of go.')
    
    parser.add_argument('--set', default='', type=str,
                        help='Set and use this version of go.')
    
    parser.add_argument('--rem', default='', type=str,
                        help='Remove a downloaded version of go.')

    args = parser.parse_args()        
    if args.list:
        list_go_versions()
    elif args.show:
        show_installed_versions()
    elif args.get:
        get_go_version(args.get)
    elif args.set:
        set_go_version(args.set) 
    elif args.rem:
        remove_installed_version(args.rem)
    elif args.version:
        print(__version__)
    else:
        parser.print_help()
        print("""
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
""")

if __name__ == '__main__':
    sys.exit(main())
