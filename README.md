![Icon](https://github.com/fnord12/service.autosub/blob/master/resources/icon.png)

AutoSub for Kodi
======

![screenshot](https://github.com/fnord12/service.autosub/blob/master/resources/fanart.jpg)

### What is it?
A service for Kodi that automatically enables subtitles based on your preferences.  This is a rework of Language Preference Manager, but instead of being as open and flexible as that program, it takes a more prescriptive approach that works for a common use case (and is easier to configure/troubleshoot).

---
### Algorithm
The service takes the following approach, in this order:

1. Checks if the current audiostream is not one of your preferred languages and is NOT undefined.  If so, it enables the best subtitle (see below), avoiding forced subtitles.

2. If the audiostream IS undefined, it will look at your list of tags and/or genres.  If the video has a tag that matches, it will enable the best subtitle.

3. If the video is in one of your preferred languages, it will look for an external forced subtitle.

4. If no external forced subtitle is found, it will look for an embedded forced subtitle.

---
## Best Subtitle
What is a best subtitle in steps #1 and #2?

* It will try to find a subtitle that matches your preferred languages, in priority order.  Failing that, it will take the first Undetermined subtitle.

* It will not pick a Forced subtitle, to the extent possible (see Caveats).

---
## Forced Subtitles
A forced subtitle is for when the audiostream is in your preferred language(s) but there is dialogue (or text) that is not in that language.  This could be a foreign language or non-human language, or it might be a translation of signs or titlecards, or even song lyrics (especially for anime).

* For external subtitles, they need to be renamed to match the External Forced Sub Indicator in the Settings.  Due to limitations (see Caveats #2), you need to pick a real language.  I've chosed the language Fula as the default (simply because it starts with F and isn't a common language for the videos i watch).  So your subtitle would need to be "MovieName.ful.srt".

* For embedded subtitles, they are determined based on Name.  See Caveats #1 for more.

---
### Setup

* Install the add-on (obviously)

* Take a look at the current settings (you will find it under My Addons > Services) and revise as needed:

SUB PREFERENCES
Preferred Language(s).  Input the three letter language codes of your preferred languages, separated by a comma.  If audio is in a preferred language, the service will only try to enable forced subtitles.  And the order of your preferred languages helps determine which subtitle to enable.

External Forced Sub Indicator.  Input a single three letter language code that will indicate that an external subtitle.  If you enter "ful", then your external sub files should be "MovieName.ful.srt".

Embedded Forced Sub Indicator.  Input words that might indicate that an embedded subtitle is forced.  The search will check all cases (e.g. foreign, Foreign, FOREIGN) and will find partial matches, (e.g. "Foreign" will find "Foreign Parts Only").

Enable subtitles for these tags.  Input the tag names and/or genres that indicate that a subtitle should be enabled.  Note that the subtitle will still only be enabled if the audiostream is unknown (see the algorithm).

ADVANCED
Log level.  Affects whether information will be written to the log all the time, or just when Debug mode is on, or only when there's an error.  Leave it alone, probably.

Turn off subtitles if no subtitle preference matched.  Explicitly turn off subtitles if the conditions in the algorithm aren't met.  Otherwise it will leave them in whatever state they were in when you last played the file (standard Kodi behavior).  Try turning this off if Caveat #4 is causing you problems.

Use Genre with Tags.  Used in Step #2.  Indicates whether you want to use just Tags, just Genres, Both, or Neither (skips step #2).

Delay the evaluation...  Enable this if you are experiencing a problem where the video is restarting itself.  This is left over from Language Preference Manager and mainly seemed to be due to changing audiostreams, so it shouldn't be necessary.  The old default was 500 (half a second) if you need to try it.

---
### Disclaimers

---
## Limitations compared to Language Preference Manager

* It does not change the audiostream.

* It does not allow different subtitles based on conditions (i.e. language A if tag is anime, language B is tag is something else).

* It won't enable subtitles based on tag/genre alone.  (This could be adjusted fairly easily; let me know if you need it.)

---
## Caveats/Challenges

1. Unfortunaely, Kodi's JSON query returns a subtitles Name, Language, and Index, but not the Forced flag.  Therefore, embedded forced subtitles can only be guessed based on the Name.  Hence the Embedded Forced Sub Indicator setting.  The default settings include every Name i could think of, but if you encounter something else you can add it.  But that's still dependent on a Name having been input at all when the video file was created.  You can use something like MKVToolNix to add a name to a video file if necessary.

2. As noted above, for external forced subs, it must be a real language recognized by Kodi and listed in the langcodes.py file.  It can't (unfortunately) just be MovieName.forced.srt or something.

3. For some reason, the JSON query that returns the subtitle Name does not provide any data when PseudoTV is running, even though it works fine for the same file outside of PseudoTV.  That means it won't be able to avoid embedded subtitles in steps 1&2, or pick them in step #4.  Handing for external subtitles still works, though. 

4. The only available Kodi function to trigger this is OnAVChange, and unfortunately Kodi counts seeking as an AVChange.  That means every time you rewind, etc., the algorithm will attempt to reapply itself.  That's not a problem if you're happy with what subtitle it is picking, but if you've manually changed the subtitle, you will have to manually change it again after seeking.

---
## Warnings

Tested in Kodi 18 Leia only.  Tested with local files only (not with streaming, not with SMBs).  It should still work in other cases; i just don't know.

