# duplicity-atmos
Atmos backend for Duplicity

This is a quick hack, and isn't packaged properly etc.

  atmosbackend.py <= the backend, put it in /usr/lib64/python2.6/site-packages/duplicity/backends/atmosbackend.py
  EsuRestApi.py <= 3rd party Python lib for Atmos, put it in /usr/lib64/python2.6/site-packages/EsuRestApi.py (from https://code.google.com/archive/p/atmos-python/)

## Configuration
```
/etc/duplicity/atmos.ini
#Hostname of endpoint
[cas00001.example.com]
uid = Full UID
secret = Secret key
```

## Usage
```
PASSPHRASE="passphrase" /usr/bin/duplicity --full-if-older-than 1M /source atmos://cas00001.example.com/path/to/storage 
```
