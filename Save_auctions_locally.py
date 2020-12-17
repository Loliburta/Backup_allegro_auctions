import sys
import requests
from AllegroApi_User import AllegroAPI
import sqlite3
from datetime import datetime
import time

conn = sqlite3.connect("RybieUdko_Aukcje_Allegro.db")
cur = conn.cursor()


cur.execute('create table items(id text, name text, slug text, description text, price num, create_date int)')
cur.execute('create table images(id text, name text, body text, slug text)')

# allegro = AllegroAPI(client_id, client_secret)


for row in allegro.get_all_offers():
    primary_image = row[2]
    item = allegro.get_offer_fields(row[0])
    print(item)

    images = [{'name': 'original_'+str(0), 'body': primary_image}, {'name': 'medium_'+str(0), 'body': primary_image.replace('original', 's400')}]
    for i, image in enumerate(item['images']):
        medium = image.replace('original', 's400')
        images.append({'name': 'original_'+str(i+1), 'body': image})
        images.append({'name': 'medium_'+str(i+1), 'body': medium})

    date = int(datetime.timestamp(datetime.strptime(item['create_date'][:-4], "%Y-%m-%d %H:%M:%S")))

    cur.execute('insert into items values(?, ?, ?, ?, ?, ?)', (item['id'], item['name'], item['slug'], item['description'], item['price'], date))

    for image in images:
        cur.execute('insert into images values(?, ?, ?, ?)', (item['id'], image['name'], image['body'], item['slug']))

    conn.commit()