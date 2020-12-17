#Z bloba do zdjecia filename.jpeg

import requests
import sqlite3

# Convert binary data to proper format and write it on Hard Disk
def writeTofile(data, filename):
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored blob data into: ", filename, "\n")



conn = sqlite3.connect("Sephiryt_Aukcje_Allegro.db")
cur = conn.cursor()

## row[0] == id
## row[1] == name
## row[2] == body
## row[3] == slug
## row[4] == photo


# Example of usage 
# for row in cur.execute("SELECT * FROM images WHERE id = 7347955575 AND name = 'original_0'"):
#     writeTofile(row[4], 'imgs/01.jpeg')