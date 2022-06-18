# Halo Infinite Observer's player detection

The program expects the input to be a camera and to be 1080p.

## Download & Usage

Go to the [Release page](https://github.com/Halocrea/infinite-obs-player-detect/releases) and follow the instructions of the latest release. 

## Requirements & Notices

If you're using OBS, you won't be able to use the built-in virtual cam, you'll have to install https://obsproject.com/forum/resources/obs-virtualcam.949/.

Once you've installed it and opened OBS, go to `tool` then click on `Virtual Cam`, and `Start`.

Notice: In OBS, the refresh rate for text sources is 1 second, which can feel a bit "unresponsive". To change it, you can install the `text-overdrive.lua` script. To do so, in OBS go to `tools` then `Scripts`. Once that's done, in the "Source" field, enter the name of the text source you'll be using to display the player names.

## Player name, color, both

Once running, the program will save the current PoV's side ("Red" or "Blue") and playername individually in `side.txt` and `player.txt`, but also combined in `side_and_player.txt`.
