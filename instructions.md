# INSTRUCTIONS:

Contents:
## OBS
## SCOREBOARD
## GENERAL THOUGHTS




## OBS
1. Click "Start Streaming" in "Controls" box (bottom right)
2. If this doesn't work, need to adjust stream key (see below)
3. If it is working, get the scoreboard up and running (see "SCOREBOARD" section below)

To adjust stream key:
1. Click "Settings" in "Controls" box (bottom right)
2. Click on "Stream" (top left)
3. Copy and paste in "Stream key" from Youtube studio (google chrome)

Check on your phone whether the stream has gone live (allow a minute or two for it to load)




## SCOREBOARD

Open run.py (N.B. shouldn't need to open any other files in this folder)

1. To link to the correct match (only needed at the start of the game):
    - Add the link from play-cricket for the game to "url" below, in the format
        url = "https:// ... "
    - Save file (ctrl+s)

2. To get the live scoreboard running (once per day unless it has crashed):
    - Press green play button (top right). Should then run all day
    - To cancel/reset, press "ctrl+c". Might have to click in the "TERMINAL" box below before "ctrl+c".



If not working:

1. Check if python script has crashed (start up again if so).
2. If still not working, get rid of the scoreboard until NT has time to fix it. To get rid, go on OBS and click the eye symbols next to "text" and "text background" to make them invisible.




## GENERAL THOUGHTS
- Leave stream on all day rather than turning on/off with sessions/rain breaks
- Can change python stuff for scoreboard without turning stream on/off
- Keep sound off (via "Audio Mixer" - don't touch, but mute if sound is on for some reason)
