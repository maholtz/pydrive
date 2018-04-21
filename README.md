# pydrive
A simple Python script for creating a google drive backup

The aim of this script is to provide a possibility to create an backup of an google drive account.

If you are interested in using this script, you need to create an Google Project account on your own (which is pretty easy).

Steps:
* Create Google Project: https://console.developers.google.com/
* Create OAuth 2.0 Client ID (Application type: other)
* Download OAuth 2.0 Client ID as client_id.json in move it to the same folder as the pydrive.py file.

Prerequisites for running pydrive.py:
* apt install git
* apt install python3-pip
* apt install python3-setuptools
* pip3 install git+https://github.com/googledrive/PyDrive.git#egg=PyDrive (see https://github.com/googledrive/PyDrive)
* sudo pip3 install --upgrade google-api-python-client

Start:
* python3 ./drive_list.py  --noauth_local_webserver
