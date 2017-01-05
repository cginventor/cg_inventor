import PyQt4.QtCore as qc

#--------------------------------------------------------------------------------------------------#
#                                      QT BASE CLASS                                               # 
#--------------------------------------------------------------------------------------------------#

class Base(object):
    '''
        The base class for all custom QT objects. Adds common signal emitting functionality.
    '''
    
    # status signals
    #
    STATUS_NORMAL  = 'statusNormal'
    STATUS_SUCCESS = 'statusSuccess'
    STATUS_ERROR   = 'statusError'
    
    def statusNormal(self, text):
        ''' 
            Emit message with NORMAL status signal.
        
        args :
            text : the message to display
        '''
        self.emit(qc.SIGNAL(Base.STATUS_NORMAL), text)


    def statusSuccess(self, text):
        ''' 
            Emit message with SUCCESS status signal.
        
        args :
            text : the message to display
        '''
        self.emit(qc.SIGNAL(Base.STATUS_SUCCESS), text)


    def statusError(self, text):
        ''' 
            Emit message with ERROR status signal.
        
        args :
            text : the message to display
        '''
        self.emit(qc.SIGNAL(Base.STATUS_ERROR), text)
        
#------------------------------------------------------------------------------------------------ -#