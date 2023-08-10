import base64
import requests
import json
import datetime
from urllib.parse import urlencode
 
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px


class SpotifyAPI(object):
   access_token = None
   access_token_expires = datetime.datetime.now()
   access_token_did_expire = True
   client_id = None
   client_secret = None
   token_url = "https://accounts.spotify.com/api/token"
 
   def __init__(self, client_id, client_secret):
       self.client_id = client_id
       self.client_secret = client_secret
  
   # Returns the base64-encoded client credentials string.
   def get_client_credentials(self):
       client_id = self.client_id
       client_secret = self.client_secret
       if client_secret == None or client_id == None:
           raise Exception("Client ID and client secret must be set")
       client_creds = f"{client_id}:{client_secret}"
       client_creds_b64 = base64.b64encode(client_creds.encode())
       return client_creds_b64.decode() #base64 encoded string
  
   # Performs client authentication and updates access token information
   def perform_auth(self):
       token_url = self.token_url
       token_data = {
           "grant_type" : "client_credentials"
       }
       client_creds_b64 = self.get_client_credentials()
       token_headers = {
           "Authorization" : f"Basic {client_creds_b64}"      
       }
       r = requests.post(token_url, data = token_data, headers = token_headers)
       if r.status_code not in range (200, 299):
           raise Exception("Could not authenticate client.")
       data = r.json()
       now = datetime.datetime.now()
       access_token = data['access_token']
       expires_in = data['expires_in'] #seconds
       expires = now + datetime.timedelta(seconds = expires_in)
       self.access_token = access_token
       self.access_token_expires = expires
       self.access_token_did_expire = expires < now
       return True
   # Gets the access token, renewing it if expired or not present.
   def get_access_token(self):
       token = self.access_token
       expires = self.access_token_expires
       now = datetime.datetime.now()
       if expires < now:
           self.perform_auth()
           return self.get_access_token()
       elif token == None:
           self.perform_auth()
           return self.get_access_token()
       return token

   # Searches for resources on Spotify using the given query and resource type.
   def search(self, query = None, resource_type = 'albums'):
       endpoint = f"https://api.spotify.com/v1/search?q={query}&type={resource_type}"
       access_token = self.get_access_token()
       headers = {
           "Authorization" : f"Bearer {access_token}"
       }
       r = requests.get(endpoint, headers = headers)
       if r.status_code not in range(200,299):
           return {}
       return r.json()
       
   # Gets a specific resource from Spotify using its ID and optional parameters.
   def get_resource(self, id, version = "v1", resource_type = "albums", resource_type2 = ''):
       endpoint = f"https://api.spotify.com/{version}/{resource_type}/{id}/{resource_type2}"
       access_token = self.get_access_token()
       headers = {
           "Authorization" : f"Bearer {access_token}"
       }
       r = requests.get(endpoint, headers = headers)
       if r.status_code not in range(200,299):
           return {}
       return r.json()
         
   # Gets album information from Spotify using its ID.
   def get_album(self, id):
       return self.get_resource(id, resource_type = "albums")
 
   # Gets tracks of an album from Spotify using its ID.
   def get_album_tracks(self, id):
       return self.get_resource(id, resource_type = "albums", resource_type2 = "tracks")
 
   # Gets artist information from Spotify using its ID.
   def get_artist(self, id):
       return self.get_resource(id, resource_type = "artists")
   
   #  Gets information about several artists from Spotify using their IDs.
   #def get_several_artist(self, id):
   #    return self.get_resource(id, resource_type = "artists")
 
   # Gets the top tracks of an artist from Spotify using their ID.
   #def get_artist_top_tracks(self, id):
   #    return self.get_resource(id, resource_type = "artists", resource_type2 = "top-tracks")
 
   # Gets albums of an artist from Spotify using their ID.
   def get_artist_albums(self, id):
       return self.get_resource(id, resource_type = "artists", resource_type2 = "albums")
 
   # Gets related artists of an artist from Spotify using their ID.
   def get_artist_related_artist(self, id):
       return self.get_resource(id, resource_type = "artists", resource_type2 = "related-artists")
 
   # Gets track information from Spotify using its ID.
   def get_track(self, id):
       return self.get_resource(id, resource_type = "tracks")
 
   # Gets track information from several tracks from Spotify using its ID.
   #def get_several_tracks(self, id):
   #    return self.get_resource(id, resource_type = "tracks")
  
   # Gets audio features of a track from Spotify using its ID.
   def get_track_audio_features(self, id):
       return self.get_resource(id, resource_type = "audio-features")
 
   # Gets playlist information from Spotify using its ID
   def get_playlist(self, id):
       return self.get_resource(id, resource_type = "playlists")
  
   # Gets track recommendations from Spotify using seed track IDs.
   #def get_recommendations(self, id):
   #    return self.get_resource(id, resource_type = "recommendations")
 
   # Gets user top items from Spotify using seed track IDs.
   #def get_user_top_items(self):
   #    return self.get_resource(resource_type = "me", id = "top", resource_type2 = "artists")
  
   # Generates a DataFrame containing audio features of tracks from a given dataset(processing albums and their tracks).
   def df(self, data):
       d = data
       data = []
       albums = []
       for album in d['items']:
           album_name = album['name']
           trim_name = album_name.split('(')[0].strip()
           if trim_name.upper() in albums:
               continue
           albums.append(trim_name.upper()) # use upper() to standardize
           BASE_URL = 'https://api.spotify.com/v1/'
           access_token = self.get_access_token()
           headers = {
               "Authorization" : f"Bearer {access_token}"
               }
           r = requests.get(BASE_URL + 'albums/' + album['id'] + '/tracks',
               headers = headers)
           tracks = r.json()['items']
           for track in tracks:
               f = requests.get(BASE_URL + 'audio-features/' + track['id'],
                   headers=headers)
               f = f.json()
               f.update({
                   'track_name': track['name'],
                   'album_name': album_name,
                   'short_album_name': trim_name,
                   'release_date': album['release_date'],
                   'album_id': album['id']
               })
               data.append(f)
       df = pd.DataFrame(data)
       df['release_date'] = pd.to_datetime(df['release_date'])
       df = df.sort_values(by='release_date')
       return df
   
   # # Generates a DataFrame containing audio features of tracks from a given dataset(individual tracks).
   def df2(self, data):
       d = data
       data = []
       tracks = []
       for track in d['items']:
           track_name = track['name']
           tracks.append(track_name)
           BASE_URL = 'https://api.spotify.com/v1/'
           access_token = self.get_access_token()
           headers = {
               "Authorization" : f"Bearer {access_token}"
               }
           r = requests.get(BASE_URL + 'tracks/' + track['id'],
               headers = headers)
           print(r)
           tracks = r.json()['items']
           for track in tracks:
               f = requests.get(BASE_URL + 'audio-features/' + track['id'],
                   headers=headers)
               f = f.json()
               f.update({
                   'track_name': track['name'],
                   #'album_name': album_name,
                   #'short_album_name': trim_name,
                   #'release_date': track['release_date'],
                   'track_id': track['id']
               })
               data.append(f)
       df = pd.DataFrame(data)
       df['release_date'] = pd.to_datetime(df['release_date'])
       df = df.sort_values(by='release_date')
       return df
   
   # Calculates the average value of a specific audio feature across all tracks in an album.
   def average(self, id, audio_feature):
        tracks = []
        data = spotify.get_album_tracks(id)
        for track in data['items']:
            #print(track['name'], ' --- ', track['id'], ' --- ')
            x = spotify.get_track_audio_features(track['id'])
        
            tracks.append(x[audio_feature])
        average = sum(tracks)/len(tracks)
        return average
    
   # Gets various metadata and features of a track from Spotify using its ID.
   def getTrackFeatures(self, id):
        meta = spotify.get_track(id)
        features = spotify.get_track_audio_features(id)
        
        # meta
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        explicit = meta['explicit']
        release_date = meta['album']['release_date']
        length = meta['duration_ms']
        popularity = meta['popularity']
        release_date = meta['album']['release_date']

        # features
        acousticness = features['acousticness']
        danceability = features['danceability']
        energy = features['energy']
        instrumentalness = features['instrumentalness']
        liveness = features['liveness']
        loudness = features['loudness']
        speechiness = features['speechiness']
        tempo = features['tempo']
        time_signature = features['time_signature']

        track = [name, album, artist, explicit, release_date, length, popularity, release_date, acousticness, danceability, energy, instrumentalness, liveness, loudness, speechiness, tempo, time_signature]
        return track

   # Gets track ids for items in a playlist
   def get_playlist_track_ids(self, playlist_id):
        ids = []
        playlist = spotify.get_playlist(playlist_id)
        for item in playlist['tracks']['items']:
            track = item['track']
            ids.append(track['id'])
        return ids

   # Creates a DataFrame from tracks in a playlist and exports it to a CSV file.
   def playlist_dataframe(self, playlist_id):
        ids = spotify.get_playlist_track_ids(playlist_id)
        tracks = []
        for i in range(len(ids)):
            track = spotify.getTrackFeatures(ids[i])
            tracks.append(track)
        df = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'explicit', 'release_date', 'length', 'popularity', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'time_signature', 'valence'])
        df["release_date"] = pd.to_datetime(df["release_date"])
        df["year"] = df["release_date"].dt.year
        df = df.sort_values(by='release_date')
        df.to_csv("playlist_dataframe.csv", sep = ',')     
        
        return df
   
   # Gets track ids for items in an album
   def get_album_track_ids(self, album_id):
        ids = []
        album = spotify.get_album(album_id)
        for item in album['tracks']['items']:
            ids.append(item['id'])
        return ids

   # Creates a DataFrame from tracks in an album and exports it to a CSV file.
   def album_dataframe(self, album_id):
        ids = spotify.get_album_track_ids(album_id)
        tracks = []
        for i in range(len(ids)):
            track = spotify.getTrackFeatures(ids[i])
            tracks.append(track)
        df = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'explicit', 'release_date', 'length', 'popularity', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'time_signature', 'valence'])
        df["release_date"] = pd.to_datetime(df["release_date"])
        df["year"] = df["release_date"].dt.year
        df = df.sort_values(by='release_date')
        df.to_csv("album_dataframe.csv", sep = ',')     
        return df

   # Gets album IDs of an artist from Spotify using their ID.
   def get_artist_album_ids(self, artist_id):
        albums_ids = []
        artist_albums = spotify.get_artist_albums(artist_id)
        for item in artist_albums['items']:
            albums_ids.append(item['id'])
        return albums_ids

   # Creates a DataFrame from tracks from an artist and exports it to a CSV file.
   def artist_dataframe(self, artist_id):
        ids = []
        artist_album_ids = spotify.get_artist_album_ids(artist_id)
        for id in artist_album_ids:
            for id in spotify.get_album_track_ids(id):
                ids.append(id)
        tracks = []
        for i in range(len(ids)):
            track = spotify.getTrackFeatures(ids[i])
            tracks.append(track)
        df = pd.DataFrame(tracks, columns = ['name', 'album', 'artist', 'explicit', 'release_date', 'length', 'popularity', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'time_signature', 'valence'])
        df["release_date"] = pd.to_datetime(df["release_date"])
        df["year"] = df["release_date"].dt.year
        df = df.sort_values(by='release_date')
        df.to_csv("artist_dataframe.csv", sep = ',')  
        return df

   # Interactive scatterplot
   def scatterplot(self, df, x_axis, y_axis):
        fig = px.scatter(df, x = x_axis, y = y_axis, color = 'album', size = 'popularity', title = "{} vs {} Correlation".format(x_axis, y_axis))
        return fig.show()

   # Correlation matrix
   def correlation(self, df):
        df = df.drop(['explicit', 'length', 'popularity', 'year'], axis = 1)
        sns.set(rc = {'figure.figsize':(12,10)})
        sns.heatmap(df.corr(), annot=True)
        return plt.show()
   
   # Line plot
   def lineplot(self, df, y_axis):
        fig = px.line(df, x = "release_date", y = y_axis)
        return fig.show()
   # Histogram of song per year
   def songs_per_year(self, df):
        fig = px.histogram(df, x = "year", title = "Songs Per Year", nbins = 50)
        return fig.show()


