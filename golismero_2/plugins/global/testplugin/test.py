
from core.plugins.iplugin import IPlugin

class TestPlugin(IPlugin):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        pass
    
    #----------------------------------------------------------------------
    def Run(self):
        """"""
        print "It'w works!"
                
        
    def CheckInputParams(self, inputParams):
        print "parameters check"
    
    def displayHelp(self):
        print "Help por test plugin"
    
    