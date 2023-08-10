from pywebio.input import *
from pywebio.output import *
from Spotify_Project import *

# Get user input for Client ID and Client Secret
client_id = input("Enter Client ID")
client_secret = input("Enter Client Secret")
spotify = SpotifyAPI(client_id, client_secret)

# Get user input to choose an option from the dropdown menu
dropdown = select("Choose an Option", ["Scatterplot", "Average for Audio Features for Tracks in Album", "Correlation Heat Map", "Audio Features Trend Over Time", "Songs Per Year"])

# Scatterplot Option
if dropdown == "Scatterplot":
    dropdown_options = select("Choose an Option", ["Playlist", "Album", "Artist"])
    id = input("Enter ID of chosen option")
    if dropdown_options == "Playlist":
        df = spotify.playlist_dataframe(id)
    if dropdown_options == "Album":
        df = spotify.album_dataframe(id)
    if dropdown_options == "Artist":
        df = spotify.artist_dataframe(id)
    x_axis = select("Choose X-Axis", ["popularity", "acousticness", "danceability", "duration_ms", "energy", "instrumentalness", "key", "liveness", "loudness", "mode", "speechiness", "tempo", "time_signature", "valence"])
    y_axis = select("Choose Y-Axis", ["popularity", "acousticness", "danceability", "duration_ms", "energy", "instrumentalness", "key", "liveness", "loudness", "mode", "speechiness", "tempo", "time_signature", "valence"])
    put_image(spotify.scatterplot(df, x_axis, y_axis))    

# Average for Audio Features Option
if dropdown == "Average for Audio Features for Tracks in Album":
    id = input("Enter Album ID")
    audio_feature = select("Choose Audio Feature", ["popularity, acousticness", "danceability", "duration_ms", "energy", "instrumentalness", "key", "liveness", "loudness", "mode", "speechiness", "tempo", "time_signature", "valence"])
    average = spotify.average(id, audio_feature)
    put_text(audio_feature, 'average is', average)

# Correlation Heat Map Option
if dropdown == "Correlation Heat Map":
    dropdown_options = select("Choose an Option", ["Playlist", "Album", "Artist"])
    id = input("Enter ID of chosen option")
    if dropdown_options == "Playlist":
        df = spotify.playlist_dataframe(id)
    if dropdown_options == "Album":
        df = spotify.album_dataframe(id)
    if dropdown_options == "Artist":
        df = spotify.artist_dataframe(id)
    put_image(spotify.correlation(df))


# Audio Features Trend Over Time Option
if dropdown == "Audio Features Trend Over Time":
    dropdown_options = select("Choose an Option", ["Playlist", "Artist"])
    id = input("Enter ID of chosen option")
    if dropdown_options == "Playlist":
        df = spotify.playlist_dataframe(id)
    if dropdown_options == "Artist":
        df = spotify.artist_dataframe(id)
    y_axis = select("Choose Y-Axis", ["popularity", "acousticness", "danceability", "duration_ms", "energy", "instrumentalness", "key", "liveness", "loudness", "mode", "speechiness", "tempo", "time_signature", "valence"])
    put_image(spotify.lineplot(df, y_axis))

# Songs Per Year Option
if dropdown == "Songs Per Year":
    dropdown_options = select("Choose an Option", ["Playlist", "Artist"])
    id = input("Enter ID of chosen option")
    if dropdown_options == "Playlist":
        df = spotify.playlist_dataframe(id)
    if dropdown_options == "Artist":
        df = spotify.artist_dataframe(id)
    put_image(spotify.songs_per_year(df))


    
    
