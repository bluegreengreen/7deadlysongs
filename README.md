# 7deadlysongs
A Python script to condense your Spotify playlist into 7 songs. It attempts to maximise the diversity of the songs it chooses (so it looks like you have an interesting taste in music!).

## Prerequisites

The script relies on **spotipy**.

Because I'm a bit of a cheapskate, you'll need to host your own app for this. Fortunately, Spotify provides a [handy guide](https://developer.spotify.com/documentation/web-api) which is fairly short and simple. Once you've done so, you'll need to paste the relevant values from your own app into the code.

## Other notes

For different results, you can toy around with the k-value and the number of iterations, or change which Audio Features the program considers. I can't guarantee that it won't blow up if you do that, though (actually, I can't guarantee it won't blow up even without any changes).

This is pretty poor code, and it was in part a revision tool for my CS course. Please do go ahead and make it better if you're interested.
