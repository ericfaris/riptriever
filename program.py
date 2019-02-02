import sys
import paramiko
import os
import fnmatch
import pickle
import re
import requests
from stat import S_ISDIR

def getExistingDirs():
    try:
        existingDirs = pickle.load(open("history.pickle", "rb"))
        return existingDirs
    except:
        return []

def putExistingDirs(existingDirs):
    if len(existingDirs) != 0: 
        if len(existingDirs) > 100:
            del existingDirs[:50]
        file = open("history.pickle", "wb")
        pickle.dump(existingDirs, file)
        file.close()

def getShows():
    shows = []
    text_file = open("shows.txt", "r")
    lines = text_file.readlines()
    for line in lines:
        shows.append(line.replace("\n",""))
    text_file.close()
    return shows

def getDirsToDownload(existingItems, shows):
    dirsToDownload = []
    items = sftp.listdir(REMOTE)
    for item in items:
        if item not in existingItems:
            for show in shows:
                p = re.compile(str(show).lower().replace(" ", ".", -1))
                m = p.match(item.lower())
                if m:
                    dirsToDownload.append(item)
                    existingItems.append(item)
    return dirsToDownload

def download_dir(remote_dir, local_dir):
    os.path.exists(local_dir) or os.makedirs(local_dir)
    dir_items = sftp.listdir_attr(remote_dir)
    for item in dir_items:
        # assuming the local system is Windows and the remote system is Linux
        # os.path.join won't help here, so construct remote_path manually
        remote_path = remote_dir + '/' + item.filename         
        local_path = os.path.join(local_dir, item.filename)
        if S_ISDIR(item.st_mode):
            download_dir(remote_path, local_path)
        else:
            t = re.search(r'.*\.mkv$|.*\.mp4$', item.filename)
            if t is not None:
                sftp.get(remote_path, local_path)

def printTotals(transferred, toBeTransferred):
    print("Transferred: {0}\tof: {1}").format(transferred, toBeTransferred)

REMOTE = "/home26/steeple05/downloads/rips"
LOCAL = "f:\\videos\\tv"
transport = paramiko.Transport(('hero.seedhost.eu', 22))
transport.connect(username='steeple05', password='KnZ2vc5weFt2wRfG')
sftp = paramiko.SFTP.from_transport(transport)
existingDirs = getExistingDirs()
shows = getShows()
dirsToDownload = getDirsToDownload(existingDirs, shows)

for dir in dirsToDownload:
    download_dir(REMOTE + "/" + dir, LOCAL)
putExistingDirs(existingDirs)
sftp.close()