# 7deadlysongs
A Python script to condense your Spotify playlist into 7 songs. It attempts to maximise the diversity of the songs it chooses (so it looks like you have an interesting taste in music!).

## Guide

### Prerequisites

- To get this working you'll need to make sure you have [Python](https://www.python.org/downloads/) installed.

- The script relies on the [spotipy](https://pypi.org/project/spotipy/) library, so you'll also need to ensure you've got that installed.

- Because I'm a bit of a cheapskate, you'll need to host your own app for this. Fortunately, Spotify provides a [handy guide](https://developer.spotify.com/documentation/web-api) which is fairly short and simple.

- Once you've done so, you'll need to locate your app's Client ID and Client Secret, found in its Settings page on the Spotify for Developers dashboard.

- Replace the empty string values for *clientID* and *clientSecret* in *7deadlysongs.py* with these values.

- You should also replace the value of *redirectURI* with a suitable URL. *"http://localhost/"* works for this.

### First Run

The first time you run the script, a few extra steps are required. You hopefully shouldn't have to do this again afterwards.

- With everything set up, you should be able to run the script in the terminal with the command *python* followed by the full path to *7deadlysongs.py*.

- If successful, a window will open in your browser asking you to authenticate the app.

- If you're using *localhost* as your Redirect URI, the program will prompt you to paste the link you were redirected to into the terminal.

## Other notes

For different results, you can toy around with the k-value and the number of iterations, or change which Audio Features the program considers. I can't guarantee that it won't blow up if you do that, though (actually, I can't guarantee it won't blow up even without any changes).

This is pretty poor code, and it was in part a revision tool for my CS course. Please do go ahead and make it better if you're interested.
