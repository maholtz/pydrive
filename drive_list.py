from __future__ import print_function

import os
import datetime
import io
import urllib.parse
import configparser

from apiclient import discovery, http
# from googleapiclient import discovery, http

from httplib2 import Http
from oauth2client import file, client, tools


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.utcfromtimestamp(t)

# @RETURN list(mimeType, fileending, isBinary)
def getMimeTypeAndFileEnding(file):
    # https://developers.google.com/drive/v3/web/manage-downloads
    # dritter parameter: binary, ja oder nein, davon abängig ist, mit 
    # welchem Format die Datei heruntergeladen werden muss
    if 'application/vnd.google-apps.document' == file['mimeType']:
        return ('application/vnd.oasis.opendocument.text', 'odt', False)
    if 'application/vnd.google-apps.presentation' == file['mimeType']:
        return ('application/vnd.oasis.opendocument.presentation', 'odp', False)
    if 'application/vnd.google-apps.spreadsheet' == file['mimeType']:
        return ('application/x-vnd.oasis.opendocument.spreadsheet', 'ods', False)
    if 'image/jpeg' == file['mimeType']:
        return ('image/jpeg', 'jpg', True)
    if 'image/png' == file['mimeType']:
        return ('image/png', 'png', True)
    if 'image/gif' == file['mimeType']:
        return ('image/gif', 'gif', True)
    if 'image/svg+xml' == file['mimeType']:
        return ('image/svg+xml', 'svg', True)
    if 'application/pdf' == file['mimeType']:
        return ('application/pdf', 'pdf', True)
    if 'video/mp4' == file['mimeType']:
        return ('video/mp4', 'mp4', True)
    if 'video/3gpp' == file['mimeType']:
        return ('video/3gpp', '3gp', True)
    if 'application/java-archive' == file['mimeType']:
        return ('application/java-archive', 'jar', True)
    if 'text/plain' == file['mimeType']:
        return ('text/plain', 'txt', False)
    if 'application/zip' == file['mimeType']:
        return ('application/zip', 'zip', True)
    if 'application/x-php' == file['mimeType']:
        return ('application/x-php', 'php', False)
    if 'application/javascript' == file['mimeType']:
        return ('application/javascript', 'js', False)
    if 'application/msword' == file['mimeType']:
        return ('application/msword', 'doc', False)
    if 'application/vnd.google-earth.kmz' == file['mimeType']:
        return ('application/vnd.google-earth.kmz', 'kmz', True)
    if 'application/vnd.google-apps.map' == file['mimeType']:
        return ('application/vnd.google-apps.map', '', True)
    if 'application/octet-stream' == file['mimeType']:
        return ('application/octet-stream', '', True)
    if 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' == file['mimeType']:
        return ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx', True)
    if 'application/vnd.google-apps.form' == file['mimeType']:
        return ('application/vnd.google-apps.form', '', True)
    if 'application/vnd.oasis.opendocument.text-template' == file['mimeType']:
        return ('application/vnd.oasis.opendocument.text-template', 'ott', True)
    if 'video/mkv' == file['mimeType']:
        return ('video/mkv', 'm4v', True)
    if 'text/x-c++src' == file['mimeType']:
        return ('text/x-c++src', 'cpp', False)    
    if 'application/vnd.google-apps.drawing' == file['mimeType']:
        return ('application/vnd.google-apps.drawing', '', True)
    
    
    # if 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' == file['mimeType']:
    #    return ('application/vnd.oasis.opendocument.text', 'odt', False)
    
    # @TODO: application/vnd.google-apps.form ?
    print('Undefined mimeType: ', file['mimeType'], file)
    # default PDF
    return ('application/pdf', 'pdf', True)


def getSubFolder(parent):
    folders = DRIVE.files().list(q="mimeType = 'application/vnd.google-apps.folder' and parents = '"+parent+"' ", corpora='user',spaces='drive').execute().get('files', [])
    return folders


def printSubFolder(parent, prePrint):
    folders = getSubFolder(parent)
    for folder in folders:
        print(prePrint, folder['name'], ' ( ', folder['id'], ' )')
        try:
            printSubFolder(folder['id'], prePrint + folder['name'] + '/')
        except:
            print('------------- ')

# string download_url: URL to download that file
# string outfile: name and path where to write the file
# return void
def downloadAndWriteFile(download_url, outfile):
    resp, content = DRIVE._http.request(download_url)
    if resp.status != 200:
        print('Die Datei ', outfile, ' konnte nicht heruntergeladen werden')
        print(resp)
    with open(outfile, 'wb') as file:
        file.write(content)

# fileArray: expected keys: name, id, modifiedTime
def downloadFile(fileArray, outputPath):
    try:
        (mimeTypeParameter, fileending, binary) = getMimeTypeAndFileEnding(fileArray)
        if (DEBUG_LEVEL > 2):
            print(fileending + ' AND ' + mimeTypeParameter)
        
        if binary:
            outfile = os.path.join(outputPath, fileArray['name'])
            download_url = 'https://www.googleapis.com/drive/v3/files/'+fileArray['id']+'?alt=media'
        else:
            outfile = os.path.join(outputPath, fileArray['name']+'.'+fileending)
            download_url = 'https://www.googleapis.com/drive/v3/files/'+fileArray['id']+'/export?'+urllib.parse.urlencode({'mimeType' : mimeTypeParameter})

        # download needed?
        if os.path.isfile(outfile):
            # check if download is needed anyway
            #print('-----')
            #print('Datei ' + outfile + ' existiert schon')
            # letzte Änderung der Datei auf der Platte
            #print('Modifikation: '  + " vs. " + fileArray['modifiedTime'])
            modifiedOnline= datetime.datetime.strptime(fileArray['modifiedTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            #print('heruntergeladen: ',  modification_date(outfile))
            #print('-----')
            
            if modifiedOnline >= modification_date(outfile):
                    # Wurde online verändert
                    # neu herungerladen
                    if (DEBUG_LEVEL > 1):
                        print('Donwload File: ' + outfile + '')
                    downloadAndWriteFile(download_url, outfile)
            else:
                if (DEBUG_LEVEL > 0):
                    print('File ' + outfile + ' has not been changed.')
                # ggf. Überlappung mit aufnahmen, d.h. wenn online geändert wurde, während die Datei heruntergeladen wurde?
                # oder prüfen mit Datum gleich, ansonsten neu herunterladen?
         
        else:
             # file does not exist, download file
             downloadAndWriteFile(download_url, outfile)
    except Exception as error:
        print(fileArray['name'], '(',outfile, ') Something went wrong. The file has not been downloaded.')
        print(error)
        print('modifiedTime: ' + fileArray['modifiedTime'])
    




# Not implemented
def downloadFolder(folder, path):
    newFolder = os.path.join(path, folder)
    if (DEBUG_LEVEL > 0):
        print('Neuer Ordner: ', newFolder)
    if not os.path.isdir(path):
        raise AssertionError();
    if not os.path.isdir(newFolder):
        os.makedirs(newFolder)
    if not os.path.isdir(newFolder):
        raise AssertionError()
    # Alle Dateien für diesen Ordner herunterladen
    
# Export all files in drive-folder 'parent'
# and download them to backup_path
#
# @TODO: maximum 1000 files per folder
def donwloadFiles(backup_path, parent):
    # @TODO: it could happen, that there are more than 1000 files per folder
    files = DRIVE.files().list(q="mimeType != 'application/vnd.google-apps.folder' and parents = '"+parent+"' ", corpora='user', spaces='drive', pageSize='1000', fields="nextPageToken, files(id, name, mimeType, kind, trashed, parents, spaces, version, modifiedTime)").execute().get('files', [])
    for f in files:
        if (DEBUG_LEVEL > 0):
            print('Daten: ',f)
            print(f['name'], "\t", f['mimeType'], f['id'])
        downloadFile(f, backup_path)
    


def getParentFolder(folderId):
    # get id
    # return folder
    
    # folders = DRIVE.files().list(q="mimeType = 'application/vnd.google-apps.folder' and parents = '"+folder+"' ", corpora='user',spaces='drive').execute().get('files', [])
    return folders

folderDictonary = {}

def folderPathForFile(id, folder):
    # @TODO: what happens, if there is more than one parent?
    if (len(id) > 1):
        print('More than one parent?')
        print(id)
    parent = id[0]
    if (parent in folderDictonary):
        if (DEBUG_LEVEL > 2):
            print('folderDictonary: ' + parent + ' is known as ' + folderDictonary[parent])
        return folderDictonary[parent]
    # @TODO: create Hash
    if (DEBUG_LEVEL > 1):
        print('Parent ID: ' + parent + " in Folder " + folder)
    
    file = DRIVE.files().get(fileId=parent, fields='parents, name, kind').execute()
    if (DEBUG_LEVEL > 2):
        print(file)
    # check if parent is root
    if ('parents' not in file):
        return folder    
    
    folder = folderPathForFile(file['parents'], file['name'] + PATH_SEPERATOR + folder)
    folderDictonary[parent] = folder
    if (DEBUG_LEVEL > 2):
        print(folderDictonary)
    return folder

# @TODO: maximum 1000 files possible
def updateBackupGoogleDrive(BACKUP_PATH, modifiedTime):
    if (DEBUG_LEVEL > 1):
        print(modifiedTime)
    # if (DEBUG_LEVEL > 0):
    #    modifiedTime = '2018-03-11T19:38:36.117974Z'
    files = DRIVE.files().list(q=" modifiedTime >= '" + modifiedTime + "' ", corpora='user', spaces='drive', pageSize='1000', fields="nextPageToken, files(id, name, mimeType, kind, trashed, parents, spaces, version, modifiedTime)").execute().get('files', [])


    if (DEBUG_LEVEL > 2):
        print(len(files))
    for f in files:
        if (DEBUG_LEVEL > 2):
            print('Daten: ',f)
            
        if ('parents' not in f):
            if (DEBUG_LEVEL > 1):
                print(f['name'], "\t", f['mimeType'], f['id'], 'NULL')
            folder = ''
        else:
            if (DEBUG_LEVEL > 1):
                print(f['name'], "\t", f['mimeType'], f['id'], f['parents'])
            folder = folderPathForFile(f['parents'], '')
            
        if (DEBUG_LEVEL > 0):
            print('Folder: ' + folder)
        
        if ('application/vnd.google-apps.folder' == f['mimeType']):
            
            newFolder = createFolder(BACKUP_PATH, folder)
            if (DEBUG_LEVEL > 1):
                print('New folder: ', newFolder)
        else:
            folder = os.path.join(BACKUP_PATH, folder)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            downloadFile(f, folder)
        
# @return String New Folder with path included
def createFolder(path, folder):
    newFolder = os.path.join(path, folder)
    if os.path.isdir(newFolder):
       return newFolder
    if not os.path.isdir(path):
        raise AssertionError();
    if not os.path.isdir(newFolder):
        os.makedirs(newFolder)
    if not os.path.isdir(newFolder):
        raise AssertionError()
    return newFolder

def fullbackupGoogleDrive(backup_path, startFolder, rekursiv):
    if not os.path.isdir(backup_path):
        raise AssertionError('Backup Path does not exists. Please create Path: ' + backup_path);
    # alle Dateien herunterladen
    donwloadFiles(backup_path, startFolder)
    if rekursiv:
        # für jedes Verzeichnis
        folders = getSubFolder(startFolder)
        for folder in folders:
            print(folder['name'], ' ( ', folder['id'], ' )')
            # Verzeichnis erstellen
            newFolder = createFolder(backup_path, folder['name'])
            fullbackupGoogleDrive(newFolder, folder['id'], rekursiv)


# https://docs.python.org/3/library/configparser.html
def writeConfig(config):
    with open(INI_FILE, 'w') as configfile:
        config.write(configfile)

def initConfig():
    config = configparser.ConfigParser()
    config.read_dict({'MAIN': {'counter': 0,
                               'version': 1,
                               'debug_level': 0,
                               'lastrun': '1970-01-01T00:00:00.000000Z',
                               'backup_path': 'backup',
                               'fullbackup': 'On'}
    })
    if os.path.isfile(INI_FILE):
        config.read(INI_FILE)
    else:
        # write default values
        print('INI File not found, creating new one: ' + INI_FILE)
        writeConfig(config)
    config.sections()
    main = config['MAIN']
    DEBUG_LEVEL = main.getint('debug_level', 0)
    
    # there is no need for that counter, it is just
    # for learning pyhton and debugging purpose
    counter = main.getint('counter', 0)
    if (DEBUG_LEVEL > 0):
        print('Counter: ' + str(counter) + ' before update')
    config['MAIN']['counter'] = str(counter+1)
    writeConfig(config)
    if (DEBUG_LEVEL > 0):
        print('Backuppath: ' + config['MAIN']['backup_path'])
        print('Counter: ' + config['MAIN']['counter'])
        print('Lastrun: ' + config['MAIN']['lastrun']);
        print('Fullbackup: ' + config['MAIN']['fullbackup']);
    return config


def initGoogleDrive():
    SCOPES = 'https://www.googleapis.com/auth/drive'
    id_file = 'client_id.json'
    storage_file = 'drive_list_storage.json'
    creds = False

    if os.path.isfile(storage_file):
        # get credentials from storage File
        store = file.Storage(storage_file)
        creds = store.get()
    
    # if credentials does not exists yet or are invalid, retrieve authorization
    if not creds or creds.invalid:
        if (DEBUG_LEVEL > 0):
            print('No credentials found')

        if os.path.isfile(id_file):
            flow = client.flow_from_clientsecrets(id_file, SCOPES)
            store = file.Storage(storage_file)
            creds = tools.run_flow(flow, store)
            print('You can remove client_id.json now')
        else: 
            # @TODO: HowTo!
            print('Client ID Configuration is missing')
            print('1. Create an new API Project at https://console.developers.google.com/')
            print('2. Create OAuth 2.0-Client-ID')
            print('3. Download JSON-File with configuration and rename it to: ', id_file)
            print('Exit Script now')
            quit()
    return discovery.build('drive', 'v3', http=creds.authorize(Http()))


# default Values
DEBUG_LEVEL = 0
INI_FILE = 'drive_list.ini'
PATH_SEPERATOR = '/'

DRIVE = initGoogleDrive()
config = initConfig()
lastrun = datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%S.%fZ")

BACKUP_PATH = config['MAIN']['backup_path']

# Check Backup path
if (not os.path.isdir(BACKUP_PATH)):
    print('Backup Folder ' + BACKUP_PATH + ' does not exist.')
    print('Please create Backup Folder: ' + BACKUP_PATH)
    quit()

if (config.getboolean('MAIN', 'fullbackup')):
    if (DEBUG_LEVEL > 0):
        print('Fullbackup!')
    fullbackupGoogleDrive(BACKUP_PATH, 'root', True)
    # We do not wan a fullbackup every time
    # just, the first time
    config['MAIN']['fullbackup'] = 'Off'
    writeConfig(config)
    if (DEBUG_LEVEL > 0):
        print('Fullbackup successful')
        print('Config was changed - fullbackup is now OFF')
else:
    if (DEBUG_LEVEL > 0):
        print('Update!')
    updateBackupGoogleDrive(BACKUP_PATH, config['MAIN']['lastrun'])
    if (DEBUG_LEVEL > 0):
        print('Update successful')

# run was successful, so write new lastrun
config['MAIN']['lastrun'] = lastrun
writeConfig(config)

# End of Script...
# next lines, just for testing

test = False
if (test):
# modifiedOnline= datetime.datetime.strptime(fileArray['modifiedTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
# AND  mimeType != 'application/vnd.google-apps.folder'

# Parameter für q
# https://developers.google.com/drive/v3/web/search-parameters

    modifiedTime = " modifiedTime >= '2018-03-01T09:41:15.359653Z' "

    files = DRIVE.files().list(q=modifiedTime + "  ", corpora='user', spaces='drive', pageSize='1000', fields="nextPageToken, files(id, name, mimeType, kind, trashed, parents, spaces, version, modifiedTime)").execute().get('files', [])
    print(files)
    print(len(files))
    for f in files:
        print('Daten: ',f)
        print(f['name'], "\t", f['mimeType'], f['id'])
        # metaData = DRIVE.files().get('file', f['id'])
        # print(metaData)
                
