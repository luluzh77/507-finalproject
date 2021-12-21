from flask import Flask, render_template, request

import main


class FlaskApp(object):
    def __init__(self):

        self.app = Flask(__name__, static_url_path='/static')
        spotify_data, twitter_data = main.read_data()
        self.graph = main.build_graph(spotify_data, twitter_data)
        main.plot_artist_twitter_popularity(self.graph)
        main.plot_artist_spotify_popularity(self.graph)
        main.plot_tweets_distribution(self.graph)
        main.plot_tracks_popularity_by_artist(self.graph)

        @self.app.route('/', methods=["GET"])
        def index():
            return render_template('index.html')

        @self.app.route('/artists', methods=["POST"])
        def artists():
            artists = main.get_all_artists(self.graph)
            return render_template('results.html', entries=artists, next='hot_tracks')

        @self.app.route('/hottracks', methods=["POST", "GET"])
        def hot_tracks():
            artist = request.args.get('name')
            tracks = main.get_hot_track_from_artist(self.graph, artist)
            return render_template('artist.html', artist=artist, entries=tracks, next='track_detail')

        @self.app.route('/trackdetail', methods=["POST", "GET"])
        def track_detail():
            track = request.args.get('name')
            tweets = main.get_tweets_from_track(self.graph, track)
            tweets = sorted(tweets, key=lambda x: x.retweet_count + x.favorite_count, reverse=True)[:10]
            return render_template('track.html', tweets=tweets, track=track.replace("/", "_"))

    def get_app(self):
        return self.app


flask_app = FlaskApp()
app = flask_app.get_app()

if __name__ == '__main__':
    app.run(debug=False)
