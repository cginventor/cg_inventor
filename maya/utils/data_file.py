import pyDev
import os
import glob
import shutil
import filecmp
from util_generic import flattenList, printTraceback

#--------------------------------------------------------------------------------------------------#

DATA_FILE_EXTENSIONS = ['xml', 'obj', 'ma']

#--------------------------------------------------------------------------------------------------#

class DataFileError(Exception):
    pass

class DataFileErrorExistsError(Exception):
    pass

#--------------------------------------------------------------------------------------------------#

def getWriteFiles(uid, extension, additionalDirs=None, show=None, asset=None, user=None, pad=3):    
    # determine environment variables
    #
    show, asset, user, dev_mode = _getEnvVars(show=show, asset=asset, user=user)
    
    if not dev_mode:
        print('\n\nYou are not in DEV mode!!! Files will be recorded to your dev area; however, your re-build\nwill not reflect these changes unless you are building from dev, or check the files in...\n\n')
    
    # determine directory paths
    #
    symlink_dir, backup_dir = _getDirs(show, asset, user=user, additionalDirs=additionalDirs, createNonExisting=True, devMode=True)
    
    # determine data file name
    #
    symlink_name = _getSymlinkFileName(asset, uid, extension)
    file_name = _getVersionedFileName(backup_dir, asset, uid, extension, user=user, increment=True, pad=pad)
    
    symlink_file_path = os.path.join(symlink_dir, symlink_name)
    file_path = os.path.join(backup_dir, file_name)
    
    # return <sym linked file (dir path and file name)>, <"backup" file>
    #
    return symlink_file_path, file_path

#--------------------------------------------------------------------------------------------------#

def getReadFile(uid, extension, additionalDirs=None, show=None, asset=None, user=None, version=None, devMode=None, inherit=False, pad=3):    
    # determine if reading "latest" file, or a versioned file
    #
    read_versioned = False
    ignoreUser=True
    if user or version:
        read_versioned = True
    if user:
        ignoreUser=False
    
    # determine environment variables
    #
    show, asset, user, dev_mode = _getEnvVars(show=show, asset=asset, user=user)
    
    # load asset inheritance if it exists
    #
    asset_inheritance = [asset]
    if inherit:
        try:
            inheritance = os.environ['ASSET_INHERITANCE'].split('#')
            if inheritance and inheritance[0] == asset:
                asset_inheritance = inheritance
        except KeyError:
            pass
    
    # force read to use specified mode
    #
    if devMode != None:
        dev_mode = devMode
    
    # loop over inheritance path, highest first
    #
    highest_asset = asset_inheritance[0]
    file_path = None
    for asset in asset_inheritance:
        # ensure parent assets are located from live area
        #
        if asset != highest_asset:
            dev_mode = False

        # determine directory paths
        #
        try:
            symlink_dir, backup_dir = _getDirs(show, asset, user=user, additionalDirs=additionalDirs, devMode=dev_mode)
        except util_dataFileError:
            if dev_mode:
                # dev builddata directories do not exist, check live area
                #
                dev_mode = False
                try:
                    symlink_dir, backup_dir = _getDirs(show, asset, user=user, additionalDirs=additionalDirs, devMode=dev_mode)
                except util_dataFileError:
                    continue
            else:
                continue

        # determine data file name/path
        #
        if read_versioned:
            file_name = _getVersionedFileName(backup_dir, asset, uid, extension, user=user, ignoreUser=ignoreUser, version=version, pad=pad)
            file_path = os.path.join(backup_dir, file_name)
        else:
            symlink_name = _getSymlinkFileName(asset, uid, extension)
            file_path = os.path.join(symlink_dir, symlink_name)

        # verify file exists - find live non-versioned file if dev one does not exist
        #
        if os.path.isfile(file_path):
            break
        else:
            if read_versioned or not dev_mode:
                file_path = None
                continue
            
            try:
                symlink_dir, backup_dir = _getDirs(show, asset, user=user, additionalDirs=additionalDirs, devMode=False)
            except util_dataFileError:
                file_path = None
                continue
            
            file_path = os.path.join(symlink_dir, symlink_name)

            if not os.path.isfile(file_path):
                file_path = None
                continue
            break
    # failed to find file_path?
    #
    if not file_path:
        raise util_dataFileExistsError('Unable to find a file matching search parameters!!!')
    
    return file_path

#--------------------------------------------------------------------------------------------------#

def createSymlink(file_path, symlink_file_path):
    if os.path.isfile(symlink_file_path):
        os.unlink(symlink_file_path)
    
    try:
        os.symlink(file_path, symlink_file_path)
    except Exception:
        raise util_dataFileError('Failed to create "latest" sym linked data file ["%s"] from source file ["%s"]!!!' %(symlink_file_path, file_path))

#--------------------------------------------------------------------------------------------------#

def publishAsset(show=None, asset=None, user=None, fileBaseNames=None, extensions=DATA_FILE_EXTENSIONS, pad=3):
    # check out files and return results
    #
    return copyAsset(srcShow=show, dstShow=show, srcAsset=asset, dstAsset=asset, srcUser=user, fileBaseNames=fileBaseNames, extensions=extensions, method='publish', pad=pad)

#--------------------------------------------------------------------------------------------------#

def checkoutAsset(show=None, asset=None, user=None, fileBaseNames=None, extensions=DATA_FILE_EXTENSIONS, pad=3):    
    # check out files and return results
    #
    return copyAsset(srcShow=show, dstShow=show, srcAsset=asset, dstAsset=asset, dstUser=user, fileBaseNames=fileBaseNames, extensions=extensions, method='checkout', pad=pad)

#--------------------------------------------------------------------------------------------------#

def copyAsset(srcShow=None, srcAsset=None, srcUser=None, dstShow=None, dstAsset=None, dstUser=None, fileBaseNames=None, extensions=DATA_FILE_EXTENSIONS, method='copy', pad=3):    
    # determine environment variables and assign src/dst if not provided
    #
    show, asset, user, dev_mode = _getEnvVars()
    
    if not isinstance(srcShow, (str, unicode)):
        srcShow = show
    if not isinstance(dstShow, (str, unicode)):
        dstShow = show
    if not isinstance(srcAsset, (str, unicode)):
        srcAsset = asset
    if not isinstance(dstAsset, (str, unicode)):
        dstAsset = asset
    if srcUser is not None:
        if not isinstance(srcUser, (str, unicode)):
            srcUser = user
    if not isinstance(dstUser, (str, unicode)):
        dstUser = user
    
    # ensure vairables are valid for the specified method, modify if applicable, return error if
    #    not, and set up args for '_copyFile'
    #
    if method == 'checkout':
        if not (srcShow == dstShow and srcAsset == dstAsset):
            raise util_dataFileError('Source and destination arguments for show and asset must match for file checkout!!!')
        srcUser = None
        copy_user = dstUser
        copy_kwargs = {'show':None, 'asset':None, 'method':'checkout', 'pad':pad}
    elif method == 'publish':
        if not (srcShow == dstShow and srcAsset == dstAsset):
            raise util_dataFileError('Source and destination arguments for show and asset must match for file publish!!!')
        dstUser = None
        if srcUser is None:
            srcUser = user
        copy_user = srcUser
        copy_kwargs = {'show':None, 'asset':None, 'method':'publish', 'pad':pad}
    else:
        if not (srcShow != dstShow or srcAsset != dstAsset or srcUser != dstUser):
            raise util_dataFileError('All source and destination arguments (show, asset, user) match!!! Nothing to copy...')
        copy_user = dstUser
        copy_kwargs = {'show':dstShow, 'asset':dstAsset, 'method':'copy', 'pad':pad}
    
    # locate source data files ('*.latest.<extension>' files), and filter by file base names, if needed
    #
    if srcUser:
        src_dir = _getDirs(srcShow, srcAsset, user=srcUser, devMode=True)[0]
    else:
        src_dir = _getDirs(srcShow, srcAsset)[0]
    if fileBaseNames is not None:
        fileBaseNames = ['.%s.' %bn for bn in flattenList(fileBaseNames)]
    
    src_file_paths = []
    for ext in extensions:
        paths = [item for sub_list in [sorted(glob.glob(os.path.join(root, '*.latest.%s' %ext))) for root, dirs, files in os.walk(src_dir)] for item in sub_list]
        if fileBaseNames is None:
            src_file_paths.append(paths)
        else:
            filtered_paths = []
            for path in paths:
                for base_name in fileBaseNames:
                    if base_name in path:
                        filtered_paths.append(path)
                        break
            src_file_paths.append(filtered_paths)
    src_file_paths = flattenList(src_file_paths)
    
    # test if files are the same - if not, copy each file to destination, keep track of
    #    successes and failures (if any)
    #
    if method == 'publish':
        dst_dir = _getDirs(dstShow, dstAsset)[0]
    else:
        dst_dir = _getDirs(dstShow, dstAsset, user=copy_user, devMode=True)[0]
    identical_files = []
    copied_files = []
    failed_files = []
    
    for src_file_path in src_file_paths:
        dst_file_path = src_file_path.replace(src_dir, dst_dir)
        if os.path.isfile(dst_file_path):
            if filecmp.cmp(dst_file_path, src_file_path):
                identical_files.append(src_file_path)
                continue
        try:
            copied_files.append(_copyFile(src_file_path, copy_user, **copy_kwargs))
        except Exception:
            printTraceback()
            failed_files.append(src_file_path)
    
    if not copied_files:
        if not identical_files:
            raise util_dataFileError('Failed to %s any files for the asset!!!' %method)
    if identical_files:
        print('\nThe following files were identical, so there was no need to %s:' %method)
        for identical_file in identical_files:
            print("'%s'" %identical_file)
    if failed_files:
        print('\nThe following files failed to %s:' %method)
        for failed_file in failed_files:
            print("'%s'" %failed_file)
        raise util_dataFileError('Some files failed to %s for the asset!!! Check script editor for details...' %method)
    print('\n')
    
    return copied_files

#--------------------------------------------------------------------------------------------------#
# 'local' functions
#--------------------------------------------------------------------------------------------------#

def _getEnvVars(show=None, asset=None, user=None):
    # determine environment variables
    #
    env_key_show = 'IKA_SHOW_NAME'
    env_key_asset = 'ASSET_NAME'
    env_key_user = 'USER'
    env_key_dev = 'PYDEV_MODE'
    
    if not isinstance(show, (str, unicode)):
        if env_key_show not in os.environ:
            raise util_dataFileError('Could not find a valid show environment variable!!!')
        show = os.environ[env_key_show]
        
    if not isinstance(asset, (str, unicode)):
        if env_key_asset not in os.environ:
            raise util_dataFileError('Could not find a valid asset environment variable!!!')
        asset = os.environ[env_key_asset]
        
    if not isinstance(user, (str, unicode)):
        if env_key_user not in os.environ:
            raise util_dataFileError('Could not find a valid user environment variable!!!')
        user = os.environ[env_key_user]
    
    dev_mode = False
    if env_key_dev in os.environ:
        dev = os.environ[env_key_dev]
        if dev is pyDev.DEV:
            dev_mode = True
    
    return show, asset, user, dev_mode

#--------------------------------------------------------------------------------------------------#

def _getDirs(show, asset, user=None, additionalDirs=None, createNonExisting=False, devMode=False):
    # determine whether finding dev or live paths
    #
    dev_bool = False
    if devMode:
        if not user:
            raise util_dataFileError('Unable to determine dev directory path without user name!!! Please provide user...')
        dev_bool = True

    # determine directory path, and make sure it exists
    #
    if dev_bool:
        dir_path_list = ['/laika', 'jobs', show, 'rapid', 'asset', 'char', asset, 'rig', 'workfile', user, 'builddata']
    else:
        dir_path_list = ['/laika', 'jobs', show, 'rapid', 'asset', 'char', asset, 'rig', 'pub', 'builddata']


    if additionalDirs:
        dir_path_list.extend(flattenList(additionalDirs))

    symlink_dir = os.path.join(*dir_path_list)
    backup_dir = os.path.join(symlink_dir, 'backup')

    if not os.path.isdir(backup_dir):
        if createNonExisting:
            os.makedirs(backup_dir)
        elif not os.path.isdir(symlink_dir):
            raise util_dataFileError('Directory ["%s"] does not exist!!!' %backup_dir)

    return symlink_dir, backup_dir

#--------------------------------------------------------------------------------------------------#

def _getSymlinkFileName(asset, uid, extension):
    return '.'.join([asset, 'rig', uid, 'latest', extension])

#--------------------------------------------------------------------------------------------------#

def _getVersionedFileName(directory, asset, uid, extension, user=None, increment=False, ignoreUser=True, version=None, pad=3):
    # make sure 'increment' and 'version' are not both used
    #
    if increment and version:
        raise util_dataFileError("kwargs 'increment' and 'version' are mutually exclusive!!! Please only use one...")
    
    # build initial file name, then ensure user is provided if ignoreUser=False,
    #    or if ignoreUser=True and increment=True
    #
    file_name_list = [asset, 'rig', uid, 'user', '001', extension]
    
    if not ignoreUser or (ignoreUser and increment):
        if not user:
            raise util_dataFileError('Unable to determine file name!!! Please provide a user name...')
        file_name_list[-3] = user            
    
    # verify directory even exists
    #
    if not os.path.isdir(directory):
        raise util_dataFileError('Directory ["%s"] does not exist!!!' %directory)
    
    # remove <user> (if ignoring), <ver>, and <extension> name tokens to find all version
    #    numbers of the correct file name
    #
    slice_index = -3
    if not ignoreUser:
        slice_index = -2
    
    prefix = '.'.join(file_name_list[:slice_index])
    if version:
        ver = int(version)
        file_search_str = '%s*%s.%s' %(prefix, str(ver).zfill(pad), extension)
    else:
        file_search_str = '%s*.%s' %(prefix, extension)
    files = glob.glob(os.path.join(directory, file_search_str))
    
    # find specified version, highest version, or incremented from highest version
    #    (depending on search parameters)
    #
    if not len(files):
        if not increment:
            raise util_dataFileError('Unable to find a file matching search parameters!!!')
        ver = 1            
    else:
        if version:
            if len(files) > 1:
                raise util_dataFileError("Multiple files match search parameters!!! Please provide user, and/or make sure it's not being ignored...")
            file_user = files[0].split('.')[-3]
        else:
            file_name_splits = [file_name.split('.') for file_name in files]
            ver_user_dict = {}
            for file_toks in file_name_splits:
                ver_user_dict[file_toks[-2]]=file_toks[-3]
            
            ver_key = sorted(ver_user_dict.keys())[-1]
            file_user = ver_user_dict[ver_key]
            ver = int(ver_key)
            
            if increment:
                ver += 1
    
    # return versioned file name
    #
    if ignoreUser:
        if not increment:
            file_name_list[-3] = file_user
        else:
            file_name_list[-3] = user
    else:
        file_name_list[-3] = user
    
    file_name_list[-2] = str(ver).zfill(pad)
    
    return '.'.join(file_name_list)

#--------------------------------------------------------------------------------------------------#

def _getInfoFromFilePath(file_path):
    # get directory and file name info
    #
    sep = os.sep
    dir_list = file_path.split(sep)[0:-1]
    
    show = dir_list[dir_list.index('jobs') + 1]
    asset = dir_list[dir_list.index('char') + 1]
    
    start_index = dir_list.index('builddata') + 1
    if len(dir_list) == start_index:
        additional_dirs = None
    else:
        if 'backup' in dir_list:
            if dir_list.index('backup') == start_index:
                additional_dirs = None
            else:
                additional_dirs = dir_list[start_index:-1]
        else:
            additional_dirs = dir_list[start_index:]
    
    file_path_split = file_path.split('.')
    uid = file_path_split[2]
    extension = file_path_split[-1]
    
    # return info
    #
    return show, asset, additional_dirs, uid, extension

#--------------------------------------------------------------------------------------------------#

def _copyFileExplicit(src_file_path, dst_file_path): 
    # verify source file and destination file are not the same file, the source file exists, and the
    #    destination directory exists
    #
    if src_file_path is dst_file_path:
        raise util_dataFileError('Destination file ["%s"] is the same as source file ["%s"]!!! Copy failed...' %(dst_file_path, src_file_path))
    
    if not os.path.isfile(src_file_path):
        raise util_dataFileExistsError('Source file ["%s"] does not exist!!!' %src_file_path)
    
    if '.' in dst_file_path:
        if not os.path.isdir(os.path.dirname(dst_file_path)):
            raise util_dataFileError('Directory for destination file ["%s"] does not exist!!!' %dst_file_path)
    else:
       raise util_dataFileError('Destination file ["%s"] does not contain a file name!!!' %dst_file_path)
    
    # copy the file, verify copy exists
    #
    try:
        shutil.copy2(src_file_path, dst_file_path)
    except Exception:
        raise util_dataFileError('Failed to copy source file ["%s"] to destination file ["%s"]!!!' %(src_file_path, dst_file_path))
     
    if not os.path.isfile(dst_file_path):
        raise util_dataFileError('Failed to copy source file ["%s"] to destination file ["%s"]!!!' %(src_file_path, dst_file_path))

#--------------------------------------------------------------------------------------------------#

def _copyFile(file_path, user, show=None, asset=None, method='copy', pad=3):    
    # verify a dev path was given if publishing, or a live path given if checking out
    #
    pub_bool = False
    if method is 'publish':
        if 'pub' in file_path:
            raise util_dataFileError('Unable to publish provided published file ["%s"]!!! Please provide a dev file instead...' %file_path)
        pub_bool = True
        show = None
        asset = None
    elif method is 'checkout':
        if not 'pub' in file_path:
            raise util_dataFileError('Unable to check out provided dev file ["%s"]!!! Please provide a published file instead...' %file_path)
        show = None
        asset = None
    else:
        method = 'copy'
    
    # find sym link source file
    #
    if not os.path.islink(file_path):
        raise util_dataFileError('Provided file ["%s"] does not have a symlink source file!!! Please provide the symlinked file...' %file_path)
    else:
        src_file_path = os.readlink(file_path)
    
    # determine various variables from file path (directories, file name info, etc)
    #
    fileShow, fileAsset, additional_dirs, uid, extension = _getInfoFromFilePath(file_path)
    
    if not show:
        show = fileShow
    if not asset:
        asset = fileAsset
    
    # get dst path and make sure it exists
    #
    if pub_bool:
        symlink_dir, backup_dir = _getDirs(show, asset, additionalDirs=additional_dirs, createNonExisting=True)
    else:
        symlink_dir, backup_dir = _getDirs(show, asset, user=user, additionalDirs=additional_dirs, createNonExisting=True, devMode=True)
    
    # determine destination file names
    #
    dst_symlink_name = _getSymlinkFileName(asset, uid, extension)
    dst_file_name = _getVersionedFileName(backup_dir, asset, uid, extension, user=user, increment=True, ignoreUser=True, pad=pad)
    
    dst_symlink_file_path = os.path.join(symlink_dir, dst_symlink_name)
    dst_file_path = os.path.join(backup_dir, dst_file_name)
    
    # copy sym link source file to dst directory with appropriate user name/versioning
    #    and create sym link
    #
    _copyFileExplicit(src_file_path, dst_file_path)
    createSymlink(dst_file_path, dst_symlink_file_path)
    
    return (dst_symlink_file_path, dst_file_path)

