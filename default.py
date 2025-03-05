import os, sys, re
import xbmc, xbmcaddon, xbmcvfs

import json

__addon__ = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonPath__ = __addon__.getAddonInfo('path')
__addonResourcePath__ = xbmcvfs.translatePath(os.path.join(__addonPath__, 'resources', 'lib'))
__addonIconFile__ = xbmcvfs.translatePath(os.path.join(__addonPath__, 'icon.png'))
sys.path.append(__addonResourcePath__)

from langcodes import *
from prefsettings import settings

settings = settings()

def debug(msg, *args):
    try: 
        xbmc.log("LPM: " + (str(msg)))
     
        for arg in args:
            print(str(arg))
    except:
        print("LPM: Error in Debugoutput")
        print(msg)
        print(args)

class LangPref_Monitor( xbmc.Monitor ):
  def __init__( self ):
      xbmc.Monitor.__init__( self )
        
  def onSettingsChanged( self ):
      settings.init()
      settings.readPrefs()

class Main:
    def __init__( self ):
        self._init_vars()
        if (not settings.service_enabled):
            debug("Service not enabled")

        settings.readPrefs()
        self._daemon()

    def _init_vars( self ):
        self.Monitor = LangPref_Monitor()
        self.Player = LangPrefMan_Player()        

    def _daemon( self ):
        while (not self.Monitor.abortRequested()):
            xbmc.sleep(500)
           
class LangPrefMan_Player(xbmc.Player) :
    
    def __init__ (self):
        debug('init')
        xbmc.Player.__init__(self)
        self.CurrentVideo = ""
        self.CurrentPath = ""
        
    def onAVChange(self):
        debug('entering onAVChange')
        
        
        if self.isPlayingVideo():
            subtitles = self.getAvailableSubtitleStreams()
            debug('Subtitles check')
            debug(subtitles)
            if subtitles:
                #self.audio_changed = False
                #switching a track too early could lead to a reopen -> start at the beginning.
                if settings.delay > 0:
                    debug("Delaying preferences evaluation")
                    xbmc.sleep(settings.delay)
                self.getDetails()
                
            else:
                debug('no subtitles')
        else:
            debug('no video playing')
    
    def getDetails(self):
        debug('entering getDetails')
        activePlayers ='{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
        json_query = xbmc.executeJSONRPC(activePlayers)
        
        json_response = json.loads(json_query)
        activePlayerID = json_response['result'][0]['playerid']
        details_query_dict = {  "jsonrpc": "2.0",
                                "method": "Player.GetProperties",
                                "params": { "properties": 
                                            ["currentaudiostream", "audiostreams", "subtitleenabled",
                                             "currentsubtitle", "subtitles" ],
                                            "playerid": activePlayerID },
                                "id": 1}
        details_query_string = json.dumps(details_query_dict)
        json_query = xbmc.executeJSONRPC(details_query_string)
        
        json_response = json.loads(json_query)
        
        debug('json_response = ', json_response)
        debug('self.CurrentVideo= ', self.CurrentVideo)
        
        #changing the subtitles triggers OnAVChange, creating a loop.  To avoid this...
        
        newPath = xbmc.getInfoLabel('Player.Filenameandpath')
        
        debug('newPath = ', str(newPath))
        debug('self.CurrentPath = ', str(self.CurrentPath))
        
        
        if newPath == self.CurrentPath:
            if json_response == self.CurrentVideo:
                debug('No change since last time, ending')
                return
        self.CurrentVideo = json_response
        self.CurrentPath = newPath
        #end loop handling
        
        if 'result' in json_response and json_response['result'] != None:
            self.selected_audio_stream = json_response['result']['currentaudiostream']
            self.fullsubinfo = json_response['result']['subtitles']
            
        genre_tags_query_dict = {"jsonrpc": "2.0",
                                 "method": "Player.GetItem",
                                 "params": { "properties":
                                            ["genre", "tag", "tvshowid"],
                                            "playerid": activePlayerID },
                                 "id": 1}
        genre_tags_query_string = json.dumps(genre_tags_query_dict)
        json_query = xbmc.executeJSONRPC(genre_tags_query_string)
        
        json_response = json.loads(json_query)
        if 'result' in json_response and json_response['result'] != None:
            tvshowid = json_response['result']['item']['tvshowid']
            debug('tvshowid: ', tvshowid)
            debug('settings.useGenre: ', settings.useGenre)
            if tvshowid == -1:
                #movie
                gt = []
                #useGenre 0 = Tags, 1 = Genre, 2 = Both, 3 = None
                if settings.useGenre == '0' or settings.useGenre == '2':
                    if 'tag' in json_response['result']['item']:
                        gt.extend(json_response['result']['item']['tag'])
                if settings.useGenre == '1' or  settings.useGenre == '2':
                    if 'genre' in json_response['result']['item']:
                        gt.extend(json_response['result']['item']['genre'])
                self.genres_and_tags = set(map(lambda x:x.lower(), gt))
                debug('Video tags/genres: {0}'.format(self.genres_and_tags))
                debug(json_response)
            else:
                #episode
                tvshow_dict = {"jsonrpc": "2.0",
                                     "method": "VideoLibrary.GetTVShowDetails",
                                     "params": { "properties":
                                                ["genre", "tag"],
                                                "tvshowid": tvshowid },
                                     "id": 1}
                genre_tags_query_string = json.dumps(tvshow_dict)
                json_query = xbmc.executeJSONRPC(genre_tags_query_string)
                
                json_response = json.loads(json_query)
                debug(json_response)
                if 'result' in json_response and json_response['result'] != None:
                    gt = []
                    if settings.useGenre == '0' or  settings.useGenre == '2':
                        if 'tag' in json_response['result']['tvshowdetails']:
                            gt.extend(json_response['result']['tvshowdetails']['tag'])
                    if settings.useGenre == '1' or  settings.useGenre == '2':
                        if 'genre' in json_response['result']['tvshowdetails']:
                            gt.extend(json_response['result']['tvshowdetails']['genre'])
                    
                    self.genres_and_tags = set(map(lambda x:x.lower(), gt))
                debug('Video tags/genres: {0}'.format(self.genres_and_tags))
        
        Tags = self.genres_and_tags
        debug('StopTag Check.  Tags: ', Tags)
        if self.findStopTag(Tags) == 0:      
            debug("Stop tag not found.  Proceeding to evalPrefs.")
            self.evalPrefs()            
        
    def evalPrefs(self):
        debug('entering evalPrefs')
        trackIndex = 0
        #availAudio = self.getAvailableAudioStreams()
        forcedExtInd = settings.forcedExtInd
        preferredLang = settings.preferredLang
                
        subtitles = self.getAvailableSubtitleStreams()
        
        Tags = self.genres_and_tags
        lang = self.selected_audio_stream['language']
        if lang == '':
            lang = 'und'
        
        debug('Subtitles: ', subtitles)
        debug('Tags: ', Tags)
        debug('lang: ', lang)
        
        if not lang in preferredLang and not lang == 'und':
            #enabling any sub to start...
            self.showSubtitles(True)
            debug("if the audio isn't preferred or undefined, enable any sub then activate the best subtitle")
            #then looking for best sub...
            self.findBestSub(subtitles)
        elif lang == 'und' and self.findTag(Tags) == 1:
            #enabling any sub to start...
            self.showSubtitles(True)
            debug("we don't know the audio language but it's in the list of tags that need subtitles.  Enable any sub then activate the best subtitle")
            #then looking for best sub...
            self.findBestSub(subtitles)
        elif forcedExtInd in subtitles:
            debug("it's probably the preferred audio, so look for an identified external forced subtitle")
            trackIndex = self.findExtSub(forcedExtInd, subtitles)
            self.setSubtitleStream(trackIndex)
            self.showSubtitles(True)
            debug('found external forced subtitle:', subtitles[trackIndex])
        else:
            if not self.fullsubinfo:
                debug("fullsubinfo is blank, so can't check names for forced indicator.  Conditions not found.")
                if settings.turnSubsOff == 'true':
                    self.showSubtitles(False)
            else:    
                debug("look for an embedded subtitle")
                EmbeddedForced = self.findforcedEmbInd(self.fullsubinfo)
                debug('EmbeddedForced: ', EmbeddedForced)
                if not EmbeddedForced == '':
                    self.setSubtitleStream(EmbeddedForced)
                    debug('found embedded forced subtitle:', subtitles[EmbeddedForced])
                    self.showSubtitles(True)
                else:
                    debug('Conditions not found')
                    if settings.turnSubsOff == 'true':
                        self.showSubtitles(False)

    def findExtSub(self, DesiredSub, subtitles):
        debug('entering findExtSub')
        i = 0
        for subtitle in subtitles:
            if subtitle == DesiredSub:
                return i
                break
            i += 1
        debug("No external forced sub found")
                    
    def findSub(self, DesiredSub):
        debug('entering findSub')
        forcedEmbdInd = settings.forcedEmbdInd
        wordcount = len(forcedEmbdInd)
        #FullSubtitleInfo = self.fullsubinfo
        
        debug('DesiredSub = ', DesiredSub)
        debug('FullSubtitleInfo = ', self.fullsubinfo)
        debug('forcedEmbdInd = ', forcedEmbdInd)
        
        if not self.fullsubinfo:
            debug ("Can't get JSON details while in PseudoTV for some reason, so we can't avoid forced embedded subs")
            subtitles = self.getAvailableSubtitleStreams()
            i = 0
            for subtitle in subtitles:
                debug('subtitle = ')
                debug(subtitle)
                if subtitle == DesiredSub:
                    debug('Match = ', i)
                    return i
                    break
                i += 1 
        else:
            debug("Making sure we're not picking a forced sub")
            for subtitle in self.fullsubinfo:
                compare = 0
                if subtitle['language'] == DesiredSub:
                    for Word in forcedEmbdInd:
                        Word = Word.upper()
                        debug('forcedEmbdInd= ',  Word)
                        FixedSubName = subtitle['name'].upper()
                        debug ('subName= ', subtitle['name'])
                        if Word not in FixedSubName:
                            debug ('Not a Forced indicator')
                            compare = compare +1
                            if compare == wordcount:
                                debug ('Confirmed not a forced subtitle')
                                return (int(subtitle['index']))
                
                            
    def findforcedEmbInd(self,subtitles):
        debug('entering findforcedEmbInd')
        forcedEmbdInd = settings.forcedEmbdInd
        preferredLang = settings.preferredLang
        preferredLang.append('und')
                    
        for Lang in preferredLang:
            debug('Lang = ', Lang)
            for subtitle in subtitles:
                if Lang == subtitle['language']:
                    for Word in forcedEmbdInd:
                        Word = Word.upper()
                        debug('Word = ', Word)
                        FixedSubName = subtitle['name'].upper()
                        if Word in FixedSubName:
                            debug('subtitle name = ', subtitle['name'])
                            return subtitle['index']
        
        debug('no matching embedded forced subtitle')
        return ''
        
    def findBestSub(self, Subtitles):
        debug('entering findBestSub')
        found = 0
        preferredLang = settings.preferredLang
        debug ('preferredLang: ', preferredLang)
        for Lang in preferredLang:
            debug ('Lang: ', Lang)
            if Lang in Subtitles:
                found = 1
                trackIndex = self.findSub(Lang)
                debug('trackIndex: ', trackIndex)
                self.setSubtitleStream(trackIndex)
                self.showSubtitles(True)
                debug('audio not preferred or undefined so enabling preferred subtitle:', Subtitles[trackIndex])
                break
        if not found == 1:
            debug('no Preferred lang subtitle found')
            if 'und' in Subtitles:
                trackIndex = self.findSub('und')
                self.setSubtitleStream(trackIndex)
                self.showSubtitles(True)
                debug('audio not preferred or undefined, no preferred sub, so enabling first undefined subtitle:', Subtitles[trackIndex])
            else:
                self.showSubtitles(True)
                debug('audio not preferred or undefined, no preferred or Und sub, so enabling a subtitle and hoping for the best')
    
    def findTag(self,Tags):
        debug('entering findTag')
        TagActivators = settings.TagActivators
        
        for desiredTag in TagActivators:
            debug ('desiredTag: ', desiredTag)
            if desiredTag in Tags:
                debug ('desiredTagMatch = ', desiredTag)
                return 1
                break
        debug('no Tag match')
        return 0
    
    def findStopTag(self,Tags):
        debug('entering findStopTag')
        TagStoppers = settings.TagStoppers
        debug('TagStoppers', TagStoppers)
        for desiredTag in TagStoppers:
            debug ('desiredTag: ', desiredTag)
            if desiredTag in Tags:
                debug ('Stop TagMatch = ', desiredTag)
                return 1
                break
        debug('no Stop Tag match')
        return 0    
   
if ( __name__ == "__main__" ):
    main = Main()
    
