import xbmc, xbmcaddon

from langcodes import *

class settings():

    def init(self):
        addon = xbmcaddon.Addon()
        
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
      self.TagStoppers = self.Convert(addon.getSetting('TagStoppers'))      