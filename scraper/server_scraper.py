import azapi
import nltk
import json
import pandas as pd
import random
import re
import requests
import time
import traceback
import unicodedata

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

#nltk.download('stopwords')
#nltk.download('punkt')

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii.decode("utf-8") 

def get_clean_lyrics(text):
    # Paroles de la chanson "title" par "artist"
    if "paroles" in text.split("\n")[0].lower():
        text = text.split("\n")[1:]
        text = "\n".join(text)

    text_tokens = word_tokenize(text)
    tokens_without_sw = [word.lower() for word in text_tokens if not word in stopwords.words("italian")]
    clean_tokens = [word for word in tokens_without_sw if re.findall(r"[^-!$%^&*()_+|~=`{}\[\]:\";'<>?,.\/]", word)]
    return " ".join(sorted(set(clean_tokens), key=clean_tokens.index))

with open('intermediate_data/artists_albums_tracks.json', 'r') as json_file:
    artists_albums_tracks = json.load(json_file)

every_artist = {"id": [], "name": [], "followers": [], "album": []}
every_album = {
    "album_id": [], 
    "album_name": [], 
    "release_date": [], 
    "total_tracks": [], 
    "track_id": [], 
    "track_name": [], 
    "duration_ms": [],
    "explicit": [], 
    "artists": [],
    "lyrics": []
}

same_albumname, same_tracks, same_artist = False, False, False

for artist, artist_info in artists_albums_tracks.items():
    for album_id in list(artist_info["albums"].keys()):
        if album_id not in every_artist["album"]:
            every_artist["id"].append(artist)
            every_artist["name"].append(artist_info["name"])
            every_artist["followers"].append(artist_info["followers"])
            every_artist["album"].append(album_id)
    
    for album, album_info in artist_info["albums"].items():
        if album not in every_album["album_id"] and "Live" not in album_info["name"] and album_info["total_tracks"] > 1:
            for track, track_info in album_info["tracks"].items():
                if "Live" not in track_info["name"]: 
                    every_album["album_id"].append(album)
                    every_album["album_name"].append(album_info["name"])
                    every_album["release_date"].append(album_info["release_date"])
                    every_album["total_tracks"].append(album_info["total_tracks"])
                    every_album["track_id"].append(track)
                    every_album["track_name"].append(track_info["name"])
                    every_album["duration_ms"].append(track_info["duration_ms"])
                    every_album["explicit"].append(track_info["explicit"])
                    every_album["artists"].append(track_info["artists"])
                    every_album["lyrics"].append(list())

artists = pd.DataFrame.from_dict(every_artist)
albums = pd.DataFrame.from_dict(every_album)

artists.to_pickle("artists.pkl")
################################################

albums_no_dups = pd.read_pickle("./track_albums.pkl")
proxy = None

counter = 0
for track in albums_no_dups.itertuples():
    if track.lyrics != []:
        continue

    counter += 1

    if counter % 2000 == 0:
        print("Salvataggio file")
        albums_no_dups.to_pickle(f"checkpoints/albums_no_dups{counter}.pkl")

    track_name = track.track_name.lower()
    track_name = track_name.split("feat.")[0]
    track_name = track_name.split("prod.")[0]
    track_name = track_name.split("skit")[0]

    track_name = remove_accents(track_name)
    track_name = "".join(re.findall(r"[a-z0-9 %$']+", track_name)).strip()

    try:
        artist_name = "".join(re.findall(r"[a-z0-9 %$]+", artists[artists.album == track.album_id].name.iloc[0].lower()))

    except KeyError as e:
        print("La canzone è probabilmente un singolo", e)
        print(track.album_id, track.track_name, API.artist, track_name)
    else:
        title_name = track_name

        print(artist_name, title_name, "in download")

        while True:
            try:
                time.sleep(2)
                lyrics = requests.get(f"https://api.lyrics.ovh/v1/{artist_name}/{title_name}")

                if lyrics.status_code == 200:
                    lyrics_text = json.loads(lyrics.text)["lyrics"]
                    albums_no_dups.at[track.Index, 'lyrics'] = get_clean_lyrics(lyrics_text)
                    print("Success!")
                    break
                elif lyrics.status_code == 404:
                    print(lyrics, "Errore")
                    albums_no_dups.at[track.Index, 'lyrics'] = "NA"
                    break
                else:
                    print(lyrics, "Errore sconosiuto")
                    albums_no_dups.to_pickle(f"checkpoints/albums_no_dups{counter}_error.pkl")
                    exit()
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                
        else:
            pass

albums_no_dups.to_pickle("albums_no_dups_final3.pkl")