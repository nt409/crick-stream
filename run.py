"""
Gets scorecard data from online and writes to .txt files for OBS live scorecard
"""
import time
from fns import get_data, write_files

# * INSTRUCTIONS for run.py (as per instructions.md), for Griff/anyone else trying to run during varsity

# Start of the game
# ! 1. Add the link from play-cricket for the game to "url" below, in the format
# !     url = "https:// ... " (just replace the existing link below)
# ! 2. Save file (ctrl+s)

# Start of each day's play:
# ! 1. Press green play button (top right)
# ! 2. If you need to cancel/reset, press "ctrl+c". Might have to click in the "TERMINAL" box below before clicking "ctrl+c".


# * CONFIG VARIABLES: "url" and "sleeptime"

# ! to update each game:
# * UR:: link to play-cricket scorecard
# Find on Cam Uni play-cricket: https://cambridgeuniversity.play-cricket.com/Matches

URL = "https://cambridgeuniversity.play-cricket.com/website/results/5690698"


# ! leave this alone!
# * sleeptime: amount of time between checks of the website (in seconds)
# fairly long sleeptime reduces number of times we spam the website, probably a good idea

SLEEP_TIME = 40


# ! don't change anything below here!

def main(url):
    """
    Gets scorecard data from online and writes to .txt files for OBS live scorecard
    """

    data = get_data(url)
    write_files(data)


if __name__ == "__main__":

    while True:
        # main(url)

        try:
            main(URL)
        except Exception as e:
            print(e)

        print("\n\n" + f"check for update in {SLEEP_TIME} seconds" + "\n\n")

        time.sleep(SLEEP_TIME)
