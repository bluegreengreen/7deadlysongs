import math
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth

k = 7
passes = 100

# Attributes with associated weights - the higher, the more important (I think) they are
attributes = {"explicit": {"numerical": False, "weight": 0.5},
              "year": {"numerical": True, "weight": 3},
              "timeSig": {"numerical": False, "weight": 1},
              "acoustic": {"numerical": True, "weight": 1},
              "speech": {"numerical": True, "weight": 1.2},
              "dance": {"numerical": True, "weight": 1.2},
              "tempo": {"numerical": True, "weight": 1.4},
              "instrumental": {"numerical": True, "weight": 1.7},
              "energy": {"numerical": True, "weight": 1.7},
              "valence": {"numerical": True, "weight": 2}
              }

# Replace these empty strings with the appropriate values for your app!

clientID = ""
clientSecret = ""
redirectURI = ""        # you can just use http://localhost/ if you need to


# Classes for holding relevant track data, and clusterings

class TrackData:
    def __init__(self, dataPoint):
        self.values = {
            "artist": dataPoint.values["artist"],
            "explicit": dataPoint.values["explicit"],
            "year": dataPoint.values["year"],
            "acoustic": dataPoint.values["acoustic"],
            "dance": dataPoint.values["dance"],
            "energy": dataPoint.values["energy"],
            "instrumental": dataPoint.values["instrumental"],
            "speech": dataPoint.values["speech"],
            "tempo": dataPoint.values["tempo"],
            "timeSig": dataPoint.values["timeSig"],
            "valence": dataPoint.values["valence"]
        }


class DataPoint:
    def __init__(self, trackID, title, artist, explicit, year):
        self.trackID = trackID
        self.title = title
        self.values = {
            "artist": artist,
            "explicit": explicit,
            "year": int(year.split("-")[0])
        }

    def addFeatures(self, acoustic, dance, energy, instrumental, speech, tempo, timeSig, valence):
        self.values.update([("acoustic", acoustic),
                            ("dance", dance),
                            ("energy", energy),
                            ("instrumental", instrumental),
                            ("speech", speech),
                            ("tempo", tempo),
                            ("timeSig", timeSig),
                            ("valence", valence)])


class Cluster:
    def __init__(self, centroid):
        self.centroid = centroid
        self.elements = []

    def insert(self, element):
        self.elements.append(element)

    def orderByProximity(self):
        tempPairs = []
        for track in self.elements:
            tempPairs.append((dissimilarity(track, self.centroid), track))
        tempPairs.sort(key=lambda x: x[0])

        self.elements = []
        for pair in tempPairs:
            self.elements.append(pair[1])


class Clustering:
    def __init__(self):
        self.clusters = []

    def getInitialCentroids(self, pointList):
        random.shuffle(pointList)
        for i in range(0, k):
            currentPoint = pointList.pop()
            newCluster = Cluster(TrackData(currentPoint))
            newCluster.insert(currentPoint)
            self.clusters.append(newCluster)


# Normalises numerical attributes such that they have mean 0 and standard deviation 1
def normalise(points):
    for attr in attributes.keys():
        if attributes[attr]["numerical"]:
            m, sd = getMeanSD(attr, points)
            rescale(m, sd, attr, points)


def getMeanSD(attr, points):
    mean = attributeMean(attr, points)

    total = 0
    for point in points:
        total += (point.values[attr] - mean) ** 2

    sd = math.sqrt(total / len(points))

    return mean, sd


def rescale(mean, sd, attr, points):
    for point in points:
        point.values[attr] = (point.values[attr] - mean) / sd


def weightedDistance(point, centroid, attr, isNumerical, weight):
    if isNumerical:
        return
    else:
        return distCategorical(point.values[attr], centroid.values[attr]) * weight


# Calculates mixed Euclidean distance between a point and a centroid.
def dissimilarity(point, centroid):
    sim = 0

    for attr in attributes.keys():
        if attributes[attr]["numerical"]:
            sim += distNumerical(point.values[attr], centroid.values[attr]) * attributes[attr]["weight"]
        else:
            sim += distCategorical(point.values[attr], centroid.values[attr]) * attributes[attr]["weight"]

    return math.sqrt(sim)


def distNumerical(v1, v2):
    return (v1 - v2) ** 2


def distCategorical(v1, v2):
    if v1 != v2:
        return 1
    else:
        return 0


def attributeMean(attr, points):
    total = 0
    for point in points:
        total += point.values[attr]

    return total / len(points)


# Used for determining a centroid value for non-numerical attributes.
def attributeMajority(attr, points):
    scores = {}

    for point in points:
        entry = point.values[attr]
        if entry in scores:
            scores[entry] += 1
        else:
            scores[entry] = 1

    return max(scores, key=scores.get)


# Returns the index of the cluster whose centroid the track is most similar to.
def getCluster(point, clusters):
    minSim = 9999  # arbitrarily high
    minIndex = -1

    for index, cluster in enumerate(clusters):
        sim = dissimilarity(point, cluster.centroid)
        if sim < minSim:
            minSim = sim
            minIndex = index

    return minIndex


def adjustCentroid(cluster):
    vals = cluster.centroid.values
    points = cluster.elements

    for attr in attributes.keys():
        if attributes[attr]["numerical"]:
            vals[attr] = attributeMean(attr, points)
        else:
            vals[attr] = attributeMajority(attr, points)


def assignment(clustering):
    clusters = clustering.clusters

    for cluster in clusters:
        points = cluster.elements
        for i in range(0, len(points)):
            point = points.pop()
            clusters[getCluster(point, clusters)].insert(point)


def refitting(clustering):
    for cluster in clustering.clusters:
        adjustCentroid(cluster)


def kMeans(clustering, iterations):
    for i in range(0, iterations):
        assignment(clustering)
        refitting(clustering)


# Picks the most central element from each cluster, (ideally) with a distinct artist.
def pickBest(clustering):
    reps = []
    artists = []
    found = False

    for cluster in clustering.clusters:
        cluster.orderByProximity()
        for track in cluster.elements:
            if track.values["artist"] not in artists:
                reps.append(track.trackID)
                artists.append(track.values["artist"])
                found = True
                break

        if not found:  # couldn't find a distinct artist
            track = cluster.elements[0]
            reps.append(track.trackID)
            artists.append(track.values["artist"])

        found = False

    return reps


# Prints every element of each cluster
def printClustering(clustering):
    print("YOUR CLUSTERS:\n")
    for count, item in enumerate(clustering.clusters):
        print("CLUSTER", count)
        for track in item.elements:
            print(track.values["artist"] + ": " + track.title)
        print("")


def main():
    IDs = []
    initialPoints = []

    print("Connecting to Spotify...")

    scope = "playlist-read-private playlist-modify-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                                                   client_id=clientID,
                                                   client_secret=clientSecret,
                                                   redirect_uri=redirectURI))

    playlist = input("Paste the URL of your playlist: ")

    try:
        results = sp.playlist_items(playlist)
    except spotipy.exceptions.SpotifyException:
        print("ERROR: Couldn't retrieve playlist. Make sure the URL is correct!")
        return

    # combine all results
    allItems = results["items"]
    while results["next"]:
        results = sp.next(results)
        allItems.extend(results["items"])

    for item in allItems:
        track = item["track"]
        IDs.append(track["id"])
        initialPoints.append(DataPoint(track["id"], track["name"], track["artists"][0]["name"], track["explicit"],
                                       track["album"]["release_date"]))

    # audio features can only be acquired in batches of 100
    audioFeatures = []
    start = 0
    end = 100
    while start < len(IDs):
        IDsSlice = IDs[start:end]
        start += 100
        end += 100
        audioFeatures = audioFeatures + sp.audio_features(IDsSlice)

    for count, item in enumerate(audioFeatures):
        initialPoints[count].addFeatures(item["acousticness"], item["danceability"], item["energy"],
                                         item["instrumentalness"], item["speechiness"], item["tempo"],
                                         str(item["time_signature"]), item["valence"])

    print("Processing your data...")
    normalise(initialPoints)

    # Generating the initial configuration
    clustering = Clustering()
    clustering.getInitialCentroids(initialPoints)
    clusters = clustering.clusters

    for i in range(0, len(initialPoints)):
        point = initialPoints.pop()
        clusters[getCluster(point, clusters)].insert(point)
    refitting(clustering)

    # Main processing
    kMeans(clustering, passes)
    topPicks = pickBest(clustering)

    newList = sp.user_playlist_create(sp.current_user()["id"], "7 deadly songs!", False, False,
                                      "A nice little selection of 7 songs to share with your friends.")
    sp.playlist_add_items(newList["id"], topPicks)

    print("Done! You can check out your 7 deadly songs here: " + newList["external_urls"]["spotify"])

    # Un-comment the line below if you want to see all of the tracks in each clustering
    # printClustering(clustering)


if __name__ == "__main__":
    main()
