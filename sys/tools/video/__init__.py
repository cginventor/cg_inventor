import subprocess
import os

import random

AVI = '.avi'
FLV = '.flv'
MKV = '.mkv'
MOV = '.mov'
MP4 = '.mp4'
MPG = '.mpg'
QT  = '.qt'
WMV = '.wmv'

EXTENSIONS = set([AVI, FLV, MKV, MOV, MP4, MPG, QT, WMV])

def openInVLC(file_path):
    return subprocess.Popen(["C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe", file_path])
 
 
all_videos = []

def findVideoFiles(folder_path):
    all_files = []
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        
        if os.path.isdir(full_path):
            all_files.extend(findVideoFiles(full_path))
            
        else:
            _, extension = os.path.splitext(filename)
            if extension not in EXTENSIONS: continue
            all_files.append(full_path)
    
    return all_files
     
        
 
def chooseRandomVideo():
    global all_videos 
    if not all_videos:
        all_videos = findVideoFiles('F:\porn')

    num_videos = len(all_videos)    
    random_selection_index = random.randrange(num_videos)
    
    openInVLC(all_videos[random_selection_index])




