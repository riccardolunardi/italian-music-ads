import pandas as pd

albums_no_dups = pd.read_pickle("albums_no_dups_final2.pkl")

na_counter = 0
song_counter = 0 
for a in albums_no_dups.itertuples():
    if a.lyrics == "NA":
        na_counter += 1
    else:
        song_counter += 1

print("NA counter:", na_counter)
print("Song counter:", song_counter)
print("Totale:", len(albums_no_dups))