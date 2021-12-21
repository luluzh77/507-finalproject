import json
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.vertList = []
        self.numVertices = 0

    def addVertex(self, vertex):
        self.numVertices = self.numVertices + 1
        self.vertList.append(vertex)

    def getVertices(self):
        return self.vertList


class Vertex:
    def __init__(self, node_type):
        self.node_type = node_type
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def get_children(self):
        return self.children


class Artist(Vertex):
    def __init__(self, image_url, page_url, follower, genres, name, spotify_popularity):
        super().__init__("Artist")
        self.image_url = image_url
        self.favorite = None
        self.retweet = None
        self.page_url = page_url
        self.follower = follower
        self.name = name
        self.spotify_popularity = spotify_popularity
        self.genres = genres

    def get_name(self):
        return self.name

    def calculate_twitter_popularity(self):
        retweet = 0
        favorite = 0
        for track in super().get_children():
            retweet += track.retweet
            favorite += track.favorite
        self.retweet = retweet
        self.favorite = favorite


class Track(Vertex):
    def __init__(self, image_url, album_name, album_url, page_url, length, name, spotify_popularity):
        super().__init__("Track")
        self.image_url = image_url
        self.album_name = album_name
        self.album_url = album_url
        self.favorite = None
        self.retweet = None
        self.page_url = page_url
        self.length = length
        self.name = name
        self.spotify_popularity = spotify_popularity

    def calculate_twitter_popularity(self):
        retweet = 0
        favorite = 0
        for tweet in super().get_children():
            retweet += tweet.retweet_count
            favorite += tweet.favorite_count
        self.retweet = retweet
        self.favorite = favorite


class Tweet(Vertex):
    def __init__(self, created_at, text, source, retweet_count, favorite_count):
        super().__init__("Tweet")
        self.created_at = created_at
        self.text = text
        self.source = source
        self.retweet_count = retweet_count
        self.favorite_count = favorite_count


def read_data():
    spotify = open('spotify.json')
    twitter = open('twitter.json')

    spotify_data = json.load(spotify)
    twitter_data = json.load(twitter)

    spotify.close()
    twitter.close()

    return spotify_data["artists"]["items"], twitter_data["data"]


def build_graph(spotify_data, twitter_data):
    graph = Graph()

    for artist in spotify_data:
        cur_artist = Artist(artist["images"][0]["url"], artist["external_urls"]["spotify"], artist["followers"]["total"],
                            artist["genres"], artist["name"], artist["popularity"])
        tracks_tweets = []
        for entry in twitter_data:
            if entry["artist_name"] == artist["name"]:
                tracks_tweets = entry["tracks"]
                break

        for track in artist["tracks"]:
            cur_track = Track(track["album"]["images"][0]["url"], track["album"]["name"], track["album"]["external_urls"]["spotify"],
                              track["external_urls"]["spotify"], track["duration_ms"],
                              track["name"], track["popularity"])
            track_tweets = []
            for entry in tracks_tweets:
                if entry["track_name"] == track["name"]:
                    track_tweets = entry["tweets"]
                    break

            for tweet in track_tweets:
                cur_tweet = Tweet(tweet["created_at"], tweet["text"], tweet["source"],
                                  tweet["retweet_count"], tweet["favorite_count"])
                cur_track.add_child(cur_tweet)
                graph.addVertex(cur_tweet)

            cur_track.calculate_twitter_popularity()

            cur_artist.add_child(cur_track)
            graph.addVertex(cur_track)

        cur_artist.calculate_twitter_popularity()
        graph.addVertex(cur_artist)

    return graph


def get_all_artists(graph):
    artists = []
    for vertex in graph.getVertices():
        if vertex.node_type == "Artist":
            artists.append(vertex)
    return artists


def get_artist(graph, artist_name):
    artists = get_all_artists(graph)
    for artist in artists:
        if artist.name == artist_name:
            return artist


def get_hot_track_from_artist(graph, artist_name):
    artist = get_artist(graph, artist_name)
    if artist is not None:
        return artist.get_children()


def get_all_tracks(graph):
    tracks = []
    for vertex in graph.getVertices():
        if vertex.node_type == "Track":
            tracks.append(vertex)
    return tracks


def get_track(graph, track_name):
    for vertex in graph.getVertices():
        if vertex.node_type == "Track":
            vertex.__class__ = Track
            if vertex.name == track_name:
                return vertex


def get_tweets_from_track(graph, track_name):
    track = get_track(graph, track_name)
    if track is not None:
        return track.get_children()


def plot_artist_twitter_popularity(graph):
    artists = get_all_artists(graph)

    twitter = [artist.favorite + artist.retweet for artist in artists]
    names = [artist.name for artist in artists]

    fig, axs = plt.subplots(figsize=(10, 5))
    axs.bar(names, twitter)
    fig.autofmt_xdate()
    plt.savefig('static/img/artist_twitter_popularity.png')


def plot_artist_spotify_popularity(graph):
    artists = get_all_artists(graph)

    spotify = [artist.spotify_popularity for artist in artists]
    names = [artist.name for artist in artists]

    fig, axs = plt.subplots(figsize=(10, 5))
    axs.bar(names, spotify)
    fig.autofmt_xdate()
    plt.savefig('static/img/artist_spotify_popularity.png')


def plot_tracks_twitter_popularity(graph, artist):
    tracks = get_hot_track_from_artist(graph, artist)

    twitter = [track.favorite + track.retweet for track in tracks]
    names = [track.name for track in tracks]

    fig, axs = plt.subplots(figsize=(10, 5))
    axs.bar(names, twitter)
    fig.autofmt_xdate()
    plt.savefig('static/img/' + artist + '_twitter_tracks.png')


def plot_tracks_spotify_popularity(graph, artist):
    tracks = get_hot_track_from_artist(graph, artist)

    spotify = [track.spotify_popularity for track in tracks]
    names = [track.name for track in tracks]

    fig, axs = plt.subplots(figsize=(10, 5))
    axs.bar(names, spotify)
    fig.autofmt_xdate()
    plt.savefig('static/img/' + artist + '_spotify_tracks.png')


def plot_tweets_distribution(graph):
    tracks = get_all_tracks(graph)
    for track in tracks:
        tweets = get_tweets_from_track(graph, track.name)
        retweet = [tweet.retweet_count for tweet in tweets]
        favorite = [tweet.favorite_count for tweet in tweets]

        fig, axs = plt.subplots(figsize=(10, 5))
        axs.scatter(retweet, favorite)
        plt.xlabel('retweet count', fontsize=10)
        plt.ylabel('favorite count', fontsize=10)
        plt.savefig('static/img/' + track.name.replace("/", "_") + '_tweets.png')


def plot_tracks_popularity_by_artist(graph):
    artists = get_all_artists(graph)
    for artist in artists:
        plot_tracks_twitter_popularity(graph, artist.name)
        plot_tracks_spotify_popularity(graph, artist.name)



if __name__ == '__main__':
    spotify_data, twitter_data = read_data()
    graph = build_graph(spotify_data, twitter_data)
    all_artist = get_all_artists(graph)
    result_artist = get_artist(graph, "The Weeknd")
    hot_tracks = get_hot_track_from_artist(graph, "The Weeknd")
    tweets = get_tweets_from_track(graph, hot_tracks[0].name)
    plot_artist_twitter_popularity(graph)
    plot_artist_spotify_popularity(graph)
    plot_tweets_distribution(graph)

