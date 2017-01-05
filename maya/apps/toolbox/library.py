import os, inspect
import cg_inventor.maya.utils.generic as util_gen
import cg_inventor.maya.apps.toolbox.page as page


class LibraryError(Exception):
    pass

# Library Data
#
_pages = {}
_path  = None

#--------------------------------------------------------------------------------------------------#

def _getPath():
    '''
        Get the path of the toolbox pages module.
    '''
    global _path
    
    if _path is None:
        toolbox_dir = os.path.dirname(os.path.abspath(__file__))        
        _path = os.path.split(os.path.split(toolbox_dir)[0])[0]
    return _path

#--------------------------------------------------------------------------------------------------#

def load(reload=False):
    ''' 
        Find and load all toolbox page classes into memory.
    '''
    global _pages
    
    # only load if _pages is empty or reload is set to True
    #
    if reload is False and len(_pages) != 0:
        return
    
    # clear pages data
    #
    _pages = {}
    
    # get path to page package
    #
    tool_path = os.path.join(_getPath(), 'tools')
    if not os.path.exists(tool_path):
        raise LibraryError("Failed to load tools library.")
    
    # get page package
    #
    cg_inventor_package = __import__('cg_inventor.maya.apps.toolbox.pages', 
                                     ['maya', 'apps', 'toolbox', 'pages'])
    maya_package    = cg_inventor_package.__dict__['maya']
    apps_package    = maya_package.__dict__['apps']
    toolbox_package = apps_package.__dict__['toolbox']
    pages_package   = toolbox_package.__dict__['pages']
    
    # get all pages
    #
    pages_modules = _findPages(pages_package)
    for page_title, page_class in pages_modules:
        _pages[page_title] = page_class

    
def _findPages(package):
    ''' 
        Recursively find all page classes in toolbox.pages module
    '''
    pages = []
    
    package_path = os.path.dirname(os.path.abspath(package.__file__))
    package_name = package.__name__
    
    for file_name in os.listdir(package_path):
        module_path = os.path.join(package_path, file_name)

        # if file is another package
        #
        if os.path.isdir(module_path):
            try:
                sub_package = __import__('%s.%s' %(package_name, file_name), 
                                         globals(), locals(), [file_name], -1)
                pages.extend(_findPages(sub_package))
            except ImportError:
                print(util_gen.formatError("Couldn't load package '%s'." %file_name))
                print(util_gen.formatError(util_gen.getTraceback()))
            continue
        
        # check file extensions and name
        #   
        module_name, module_ext = os.path.splitext(file_name)
        if module_ext != '.py': continue
        if module_name == '__init__': continue
        
        module = __import__('%s.%s' %(package_name, module_name), 
                            globals(), locals(), [module_name], -1)
        
        for name, clss in module.__dict__.items():
            try:
                base_classes = clss.__bases__
            except AttributeError:
                continue
        
            if page.Page in base_classes:
                pages.append((name, clss))

    return pages

#--------------------------------------------------------------------------------------------------#

def reload(page_name):
    '''
        Reload the given module name.
    '''
    try:
        page_class = _pages[page_name]
    except KeyError:
        return 
    
    page_module = inspect.getmodule(page_class)
    page_names = []
    for name, clss in page_module.__dict__.items():        
        try:
            base_classes = clss.__bases__
        except AttributeError:
            continue
        
        if page.Page in base_classes:
            page_names.append(name)
                    
    reload(page_module)
    
    for page_name in page_names:
        print 'resetting', page_name
        _pages[page_name] = page_module.__dict__[page_name]

#--------------------------------------------------------------------------------------------------#

def exists(page_name):
    '''
        Returns True if the requested page exists.
    '''
    try:
        _pages[page_name]
    except KeyError:
        return False
    return True
    
#--------------------------------------------------------------------------------------------------#

def all(titles=False, classes=True):
    '''
        Return all page classes in memory.
    '''
    if titles and classes:
        return _pages.items()
    if titles and not classes:
        return _pages.keys()
    if not titles and classes:
        return _pages.values()

#--------------------------------------------------------------------------------------------------#

def clear():
    global _pages
    _pages = {}

#--------------------------------------------------------------------------------------------------#

def Page(page_name, *args, **kwargs):
    '''
        Creates an instance of the requested page class and returns it.
    '''
    if not exists(page_name):
        raise LibraryError("The requested page '%s' does not exist." %page_name)
    
    return _pages[page_name](*args, **kwargs)
    




















    