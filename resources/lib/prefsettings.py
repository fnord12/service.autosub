import xbmc, xbmcaddon

from langcodes import *

class settings():

    def init(self):
        addon = xbmcaddon.Addon()
        self.logLevel = addon.getSetting('log_level')
        if self.logLevel and len(self.logLevel) > 0:
            self.logLevel = int(self.logLevel)
        else:
            self.logLevel = LOG_INFO
            
        self.service_enabled = addon.getSetting('enabled') == 'true'
    
    def __init__( self ):
        self.init()
        
    def Convert(self, origList): 
        newList = list(origList.split(",")) 
        return newList
        
    def readPrefs(self):
      addon = xbmcaddon.Addon()    

      self.delay = int(addon.getSetting('delay'))
      self.turnSubsOff = addon.getSetting('turnSubsOff')
      self.useGenre = addon.getSetting('useGenre')
      
      self.forcedExtInd = addon.getSetting('forcedExtInd')
      self.forcedEmbdInd = self.Convert(addon.getSetting('forcedEmbdInd'))
      self.preferredLang = self.Convert(addon.getSetting('preferredLang'))
      self.TagActivators = self.Convert(addon.getSetting('TagActivators'))      
