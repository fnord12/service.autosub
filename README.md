![Icon](https://github.com/fnord12/service.autosub/blob/master/resources/icon.png)

AutoSub for Kodi 21 Omega
======

![screenshot](https://github.com/fnord12/service.autosub/blob/master/resources/fanart.jpg)

## What is it?
A service for Kodi that automatically enables subtitles based on your preferences.  This is a rework of Language Preference Manager by Ace, but instead of being as open and flexible as that program, it takes a more prescriptive approach that works for a common use case (mine! :smiley: ) and is easier to configure/troubleshoot.

In addition to providing a straightforward algorithm, it attempts to address the problem of Undetermined audiostream and subtitles, and has a (hacky) way of identifying external forced subtitles (which otherwise isn't possible).  It also improves on Language Preference Manager by looking at the TVShow tags when dealing with episodes (since episodes can't be tagged).

---
## Algorithm
The service takes the following approach, in this order:

1. Checks if the current audiostream is not one of your preferred languages and is NOT undefined.  If so, it enables the best subtitle (see below), avoiding forced subtitles.

2. If the audiostream IS undefined, it will look at your list of tags and/or genres.  If the video has a tag that matches, it will enable the best subtitle.

3. If the video is in one of your preferred languages, it will look for an external forced subtitle.

4. If no external forced subtitle is found, it will look for an embedded forced subtitle.

---
### Best Subtitle
What is a best subtitle in steps #1 and #2?

* It will try to find a subtitle that matches your preferred languages, in priority order.  Failing that, it will take the first Undetermined subtitle.

* It will not pick a Forced subtitle, to the extent possible (see Caveats).

---
### Forced Subtitles
A forced subtitle is for when the audiostream is in your preferred language(s) but there is dialogue (or text) that is not in that language.  This could be a "foreign" language or non-human fantasy language, or it might be a translation of signs or titlecards, or even song lyrics (especially for anime).

* For external subtitles, they need to be renamed to match the External Forced Sub Indicator in the Settings.  Due to limitations (see Challenge #2), you need to pick a real language.  I've chosed the language Fula as the default (simply because it starts with F and isn't a common language for the videos i watch).  So your subtitle would need to be "MovieName.ful.srt".

* For embedded subtitles, they are determined based on Name.  See Challenge #1 for more.

---
## Setup

* Install the add-on (obviously)

* Take a look at the current settings (you will find it under My Addons > Services) and revise as needed:

	* SUB PREFERENCES
		* __Preferred Language(s).__  Input the three letter language codes of your preferred languages, separated by a comma.  If audio is in a preferred language, the service will only try to enable forced subtitles.  And the order of your preferred languages helps determine which subtitle to enable.

		* __External Forced Sub Indicator.__  Input a single three letter language code that will indicate that an external subtitle.  If you enter "ful", then your external sub files should be "MovieName.ful.srt".

		* __Embedded Forced Sub Indicator.__  Input words that might indicate that an embedded subtitle is forced.  The search will check all cases (e.g. foreign, Foreign, FOREIGN) and will find partial matches, (e.g. "Foreign" will find "Foreign Parts Only").

		* __Enable subtitles for these tags.__  Input the tag names and/or genres that indicate that a subtitle should be enabled.  Note that the subtitle will still only be enabled if the audiostream is unknown (see the algorithm).  If you don't want to use tags, you can set "Use Genre with Tags" to None rather than delete the defaults.  Input your actual tag names in lowercase; spaces are ok.

	* ADVANCED
		* __Log level.__  Affects whether information will be written to the log all the time, or just when Debug mode is on, or only when there's an error.  Leave it alone, probably.

		* __Turn off subtitles if no subtitle preference matched.__  Explicitly turn off subtitles if the conditions in the algorithm aren't met.  Otherwise it will leave them in whatever state they were in when you last played the file (standard Kodi behavior).  Try turning this off if Challenge #4 is causing you problems.

		* __Use Genre with Tags.__  Used in Step #2.  Indicates whether you want to use just Tags, just Genres, Both, or Neither (skips step #2).

		* __Delay the evaluation.__..  Enable this if you are experiencing a problem where the video is restarting itself.  This is left over from Language Preference Manager and mainly seemed to be due to changing audiostreams, so it shouldn't be necessary.  The old default was 500 (half a second) if you need to try it.

* Make sure you rename your external subs to match the External Forced Sub Indicator.

---
## Caveats:

### Limitations compared to Language Preference Manager

* It does not change the audiostream.

* It does not allow different subtitles based on conditions (i.e. language A if tag is anime, language B if something else).

* It won't enable subtitles based on tag/genre alone.  (This could be adjusted fairly easily; let me know if you need it.)

---
### Challenges

1. Unfortunaely, Kodi's JSON query returns a subtitle's Name, Language, and Index, but not the Forced flag.  Therefore, embedded forced subtitles can only be guessed based on the Name.  Hence the Embedded Forced Sub Indicator setting.  The default settings include every Name i could think of, but if you encounter something else you can add it.  But that's still dependent on a Name having been input at all when the video file was created.  You can use something like MKVToolNix to add a name to a video file if necessary.

2. As noted above, for external forced subs, it must be a real language recognized by Kodi and listed in the langcodes.py file.  It can't (unfortunately) just be MovieName.forced.srt or something.

3. For some reason, the JSON query that returns the subtitle Name does not provide any data when PseudoTV is running, even though it works fine for the same file outside of PseudoTV.  That means it won't be able to avoid embedded subtitles in steps 1&2, or pick them in step #4.  Handing for external subtitles still works, though. 

4. The only available Kodi function to trigger this is OnAVChange, and unfortunately Kodi counts seeking as an AVChange.  That means every time you rewind, etc., the algorithm will attempt to reapply itself.  That's not a problem if you're happy with what subtitle it is picking, but if you've manually changed the subtitle, you will have to manually change it again after seeking.

---
### Warnings

Tested in Kodi 21 Omega.  Tested with local files only (not with streaming, not with SMBs).  It may still work in other cases (it should work to the same extent that Language Preference Manager did); i just can't test or troubleshoot.

