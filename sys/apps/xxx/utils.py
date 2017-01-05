import os
import cg_inventor.sys.utils.video as video; reload(video)


def getVideoFiles(folder_path):
    all_video_files = []
    for file_name in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file_name)
        
        if os.path.isdir(full_path):
            all_video_files.extend(getVideoFiles(full_path))
            
        else:
            extension = os.path.splitext(file_name)[1].lower()
            if extension not in video.EXTENSIONS: continue            
            all_video_files.append(full_path)
            
    return all_video_files

