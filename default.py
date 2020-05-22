import os, sys, re
import xbmc, xbmcaddon

import json

__addon__ = xbmcaddon.Addon()
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__addonname__ = __addon__.getAddonInfo('name')
__addonPath__ = __addon__.getAddonInfo('path')
__addonResourcePath__ = xbmc.translatePath(os.path.join(__addonPath__, 'resources', 'lib'))
__addonIconFile__ = xbmc.translatePath(os.path.join(__addonPath__, 'icon.png'))
sys.path.append(__addonResourcePath__)

from langcodes import *
from prefsettings import settings

settings = settings()

LOG_NONE = 0
LOG_ERROR = 1
LOG_INFO = 2
LOG_DEBUG = 3

def debug(msg, *args):
    try:
        txt=u''
        msg=unicode(msg)
        for arg in args:
            if type(arg) == int:
                arg = unicode(arg)
            if type(arg) == list:
                arg = unicode(arg)
            txt = txt + u"/" + arg
        if txt == u'':
            xbmc.log(u"LPM: {0}".format(msg).encode('ascii','xmlcharrefreplace'), xbmc.LOGDEBUG)
        else:
            xbmc.log(u"LPM: {0}#{1}#".format(msg, txt).encode('ascii','xmlcharrefreplace'), xbmc.LOGDEBUG)
    except:
        print "LPM: Error in Debugoutput"
        print msg
        print args

    
def log(level, msg):
    if level <= settings.logLevel:
        if level == LOG_ERROR:
            l = xbmc.LOGERROR
        elif level == LOG_INFO:
            l = xbmc.LOGINFO
        elif level == LOG_DEBUG:
            l = xbmc.LOGDEBUG
        xbmc.log("[Language Preference Manager]: " + str(msg), l)


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
            log(LOG_INFO, "Service not enabled")

        settings.readPrefs()
        self._daemon()

    def _init_vars( self ):
        self.Monitor = LangPref_Monitor()
        self.Player = LangPrefMan_Player()        

    def _daemon( self ):
        while (not xbmc.abortRequested):
            xbmc.sleep(500)
           
class LangPrefMan_Player(xbmc.Player) :
    
    def __init__ (self):
        debug('init')
        xbmc.Player.__init__(self)
        self.CurrentVideo = ""
        
    def onAVChange(self):
        debug('entering onAVChange')
        if self.isPlayingVideo():
            subtitles = self.getAvailableSubtitleStreams()
            debug('subtitle check: ', subtitles)
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
            debug("if the audio isn't english or undefined, activate the best subtitle")
            self.findBestSub(subtitles)
        elif lang == 'und' and self.findTag(Tags) == 1:
            debug("we don't know the audio language but it's in the list of tags that need subtitles")
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
                debug('subtitle = ', subtitle)
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
    
    def getDetails(self):
        debug('entering getDetails')
        activePlayers ='{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
        json_query = xbmc.executeJSONRPC(activePlayers)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
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
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        
        debug('json_response = ', json_response)
        debug('self.CurrentVideo= ', self.CurrentVideo)
        
        #changing the subtitles triggers OnAVChange, creating a loop.  To avoid this...
        if json_response == self.CurrentVideo:
            debug('No change since last time, ending')
            return
        self.CurrentVideo = json_response
        
        if json_response.has_key('result') and json_response['result'] != None:
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
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = json.loads(json_query)
        if json_response.has_key('result') and json_response['result'] != None:
            tvshowid = json_response['result']['item']['tvshowid']
            debug('tvshowid: ', tvshowid)
            if tvshowid == -1:
                #movie
                gt = []
                debug('settings.useGenre: ', settings.useGenre)
                #useGenre 0 = Tags, 1 = Genre, 2 = Both, 3 = None
                if settings.useGenre == '0' or settings.useGenre == '2':
                    if json_response['result']['item'].has_key('tag'):
                        gt.extend(json_response['result']['item']['tag'])
                if settings.useGenre == '1' or  settings.useGenre == '2':
                    if json_response['result']['item'].has_key('genre'):
                        gt.extend(json_response['result']['item']['genre'])
                self.genres_and_tags = set(map(lambda x:x.lower(), gt))
                log(LOG_DEBUG, 'Video tags/genres: {0}'.format(self.genres_and_tags))
                log(LOG_DEBUG, json_response )
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
                json_query = unicode(json_query, 'utf-8', errors='ignore')
                json_response = json.loads(json_query)
                log(LOG_DEBUG, json_response )
                if json_response.has_key('result') and json_response['result'] != None:
                    gt = []
                    if settings.useGenre == '0' or  settings.useGenre == '2':
                        if json_response['result']['tvshowdetails'].has_key('tag'):
                            gt.extend(json_response['result']['tvshowdetails']['tag'])
                    if settings.useGenre == '1' or  settings.useGenre == '2':
                        if json_response['result']['tvshowdetails'].has_key('genre'):
                            gt.extend(json_response['result']['tvshowdetails']['genre'])
                    
                    self.genres_and_tags = set(map(lambda x:x.lower(), gt))
                log(LOG_DEBUG, 'Video tags/genres: {0}'.format(self.genres_and_tags))
        self.evalPrefs()        
            
if ( __name__ == "__main__" ):
    log(LOG_INFO, 'service {0} version {1} started'.format(__addonname__, __addonversion__))
    main = Main()
    log(LOG_INFO, 'service {0} version {1} stopped'.format(__addonname__, __addonversion__))
