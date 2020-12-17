import requests
import sqlite3

# writeTofile(convertToBinaryData('imgs/1.jpeg'), 'zdjecie.jpeg')
def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

# add row to table
# cur.execute("ALTER TABLE images ADD COLUMN photo BLOB") 

conn = sqlite3.connect("RybieUdko_Aukcje_Allegro.db")
cur = conn.cursor()
cur2 = conn.cursor()
i = 1

for row in cur.execute('SELECT * FROM images' ):
    
    #Sciaganie nowego zdjecia z linku allegro
    with open('imgs/1.jpeg','wb') as f:
        f.write(requests.get(row[2]).content)
        
    #Zamienianie zdjecia na binary
    blob = convertToBinaryData('imgs/1.jpeg')
    
    #Wrzucanie binary zdj do bazy danych
    query = (f"UPDATE images SET photo = ? WHERE id = ? AND name = ?")
    params = (blob, row[0], row[1])
    cur2.execute(query, params)
    
    print(f"zdjecie nr {i} zostalo przeslane")
    i += 1
conn.commit()
print("Przesylanie zakonczone")
