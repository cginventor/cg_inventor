import os, sys, types

#--------------------------------------------------------------------------------------------------#

def unloadModules(*paths):
    '''
        Unload any modules loaded from the the given root file path.
    
    args :
        paths : one or more parts of a file path
    '''
    
    if len(paths) == 0: return
    
    # error check paths
    #
    for path in paths:
        if not isinstance(path, (str, unicode, int, float)):
            raise TypeError("Requires a string or unicode. Got '%s'." %type(root))
    
    # create root path
    #
    root_path = os.path.join(*paths)
    
    # check that path exists
    #
    if not os.path.exists(root_path):
        raise RuntimeError("Root Path '%s' does not exist." %root_path)
 
    # find matching modules
    #       
    modules = []    
    for item in sys.modules:
        if item in sys.builtin_module_names:
            continue
        
        module = sys.modules[item]
        if isinstance(module, types.ModuleType):
            if not hasattr(module, '__file__'):
                continue
            
            if root_path in module.__file__:
                modules.append(item)

    # remove modules
    #
    for item in modules:
        del(sys.modules[item])
        
#--------------------------------------------------------------------------------------------------#