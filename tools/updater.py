# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from subprocess import Popen, PIPE

# Put new packages inside this dictionary. package: version
needed_packages = {
    'Django': '1.6.2',
    'MySQL-python': '1.2.5',
    'django-classy-tags': '0.5',
    'ipython': '2.0.0',
    'pep8': '1.5.6',
    'psycopg2': '2.5.2',
    'readline': '6.2.4.1',
    'pysqlite': '2.6.3',
    'django-sekizai': '0.7',
    'fake-factory': '',
    'django-tinymce': '',
    'django-paypal': '',
    'South': '',
    'bleach': '',
    'django-downtime': '',
    'mangopaysdk': '',
    'django_iban': '0.2.6',
    'celery': '3.0.12',
    'sphinx': '1.2.2',
    'django-model-utils': '1.4.0',
    'django-storages': '1.1.8',
    'django-mangopay': '',
    '-e git+https://github.com/izquierdo/python-money.git@53d1bc52fe08ea778398173add1af41e2f74377b#egg=python_money --upgrade': '',
    }

subproc = Popen(['pip', 'freeze', '-l'], stdout=PIPE)
installed_packages = subproc.stdout.read().decode('utf8')

if installed_packages.isspace() or installed_packages == '':
    print('No packages already installed.'.encode('utf8'))
else:
    print('\033[1;4;96mInstalled packages:\x1b[0m'.encode('utf8'))
    print(installed_packages)
    # If on Windows, because Windows has \r\n (not tested)
    installed_packages = installed_packages.replace('\r', '').split('\n')
    installed_packages = {
        p.split('==')[0]: p.split('==')[1]
        for p in installed_packages if p != ''
        }

final_list = []

for n_package, n_version in needed_packages.iteritems():
    if n_package in installed_packages:  # Check the installed module version
        print('\033[1;95mFound package "' + n_package + '" ', end='')
        # If version doesn't matter
        if n_version == '':
            print('\033[1;4;93mVersion not specified (may be dangerous...)'
                  '\x1b[0m')
            continue
        # If versions are different
        if n_version != installed_packages[n_package]:
            print('\033[93mVersions don\'t match: <INSTALLED: '
                  + installed_packages[n_package]
                  + '> <NEEDED: ' + n_version + '>.'
                  + ' Added to install list.')
            final_list.append(n_package + "==" + n_version)
        else:
            print("\033[92mVersions match !")
    else:  # We need to install the module
        if n_version == '':  # If version doesn't matter
            print('\033[91m"' + n_package + '" not installed.'
                  + ' Added to install list.'
                  + ' \033[1;4;93mVersion not specified (may be dangerous...)')
            final_list.append(n_package)
        else:
            print('\033[91m"' + n_package + ' (' + n_version
                  + ')" not installed.'
                  + ' Added to install list.')
            final_list.append(n_package + "==" + n_version)
    print('\x1b[0m', end='')

for package in final_list:
    print('\n\033[1;4;93mWORKING ON: ' + package + '\x1b[0m')
    Popen(['pip', 'install', package]).wait()
    print('\n\033[1;4;92m' + package + ' UPDATED/INSTALLED\x1b[0m')

print('\n\033[1;4;92mWork finished!\x1b[0m')
