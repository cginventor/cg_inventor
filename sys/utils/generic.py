import inspect, os, sys, traceback

#--------------------------------------------------------------------------------------------------#

def getFunctionName():
    '''
        Returns name of calling function.
    '''
    try:
        name = inspect.stack()[1][3]
    except:
        name = "Unknown Function"
    return name

#--------------------------------------------------------------------------------------------------#

def getTypeName(obj):
    '''
        Returns python object type as a string.
    '''
    try:
        name = type(obj).__name__
    except:
        name = 'unknown'
    return name

#--------------------------------------------------------------------------------------------------#

def flattenList(input):
    '''
        Flatten list and sub lists.
    '''
    if hasattr(input, '__iter__'):
        return [item for sub_list in input for item in flattenList(sub_list)]
    else:
        return [input]

#--------------------------------------------------------------------------------------------------#

def getTraceback(last=False):
    '''
        Get the most recent traceback message.
    '''
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
    
    if last:
        last_traceback = []
        last_traceback.append(tb[0])
        
        for trace in tb[2:]:
            last_traceback.append(trace)
            
        tb = last_traceback
        
    return ''.join(tb)

#--------------------------------------------------------------------------------------------------#

def callbackPlus(callback, start_value, end_value):
    '''
        For use with callback functions. Takes a value between 0 - 100, an returns it interpolated
        between the start and end values.
    '''
    return lambda x : callback(start_value + ((end_value - start_value) * (x / 100.0)))
    
    
def callbackSetup(intervals, callback_range=100.0):
    callback_increment = float(callback_range) / intervals
    callback_counter   = [0]
    
    return callback_counter, callback_increment


def callbackCounter(counter, increment):
    counter[0] += 1
    return counter[0] * increment

#--------------------------------------------------------------------------------------------------#


