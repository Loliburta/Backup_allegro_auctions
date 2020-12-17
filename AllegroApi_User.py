# Przed uzyciem na nowym kliencie wyczyscic pliki textowe access_token i expiration_date

import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
import datetime
import sqlite3
import slugify


class AllegroAPI():
    access_token_did_expire = True
    client_id = None
    client_secret = None
    DEFAULT_OAUTH_URL = 'https://allegro.pl/auth/oauth'
    DEFAULT_REDIRECT_URI = 'http://localhost:8000'
    api_url = 'https://api.allegro.pl/'
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret     
# Authorizationon ####################################################################################      
    def get_access_code(self):
        oauth_url = self.DEFAULT_OAUTH_URL
        redirect_uri = self.DEFAULT_REDIRECT_URI
        client_id = self.client_id
        client_secret = self.client_secret
        auth_url = '{}/authorize' \
                '?response_type=code' \
                '&client_id={}' \
                '&api-key={}' \
                '&redirect_uri={}'.format(oauth_url, client_id, client_secret, redirect_uri)
    
        parsed_redirect_uri = requests.utils.urlparse(redirect_uri)

        server_address = parsed_redirect_uri.hostname, parsed_redirect_uri.port

        class AllegroAuthHandler(BaseHTTPRequestHandler):
            def __init__(self, request, address, server):
                super().__init__(request, address, server)

            def do_GET(self):
                self.send_response(200, 'OK')
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                self.server.path = self.path
                self.server.access_code = self.path.rsplit('?code=', 1)[-1]

        print('server_address:', server_address)
        webbrowser.open(auth_url)
        httpd = HTTPServer(server_address, AllegroAuthHandler)
        print('Waiting for response with access_code from Allegro.pl (user authorization in progress)...')
        httpd.handle_request()
        httpd.server_close()
        _access_code = httpd.access_code
        print('Got an authorize code: ', _access_code)
        
        return _access_code     
    
    def perform_auth(self, access_code):
        redirect_uri= self.DEFAULT_REDIRECT_URI
        oauth_url= self.DEFAULT_OAUTH_URL
        client_id = self.client_id
        client_secret = self.client_secret
        
        token_url = oauth_url + '/token'
        access_token_data = {'grant_type': 'authorization_code', 'code': access_code, 'redirect_uri': redirect_uri}
        token_result = requests.post(url=token_url, auth=requests.auth.HTTPBasicAuth(client_id, client_secret), data=access_token_data)
        
        token_object = token_result.json()
        time_now = datetime.datetime.now() 
        token_expires_in = token_object['expires_in']
        expires = time_now + datetime.timedelta(seconds=token_expires_in)
        
        with open('access_token', 'w') as f:
            f.write(token_object['access_token'])
        with open('expiration_date', 'w') as f:
            f.write(str(expires))
        self.access_token_did_expire = expires < time_now
        return True
    
    def get_access_token(self):
        with open('access_token') as f:
            token = f.readline()
        with open('expiration_date') as f:
            expires = datetime.datetime.strptime(f.readline(), "%Y-%m-%d %H:%M:%S.%f")
        time_now = datetime.datetime.now()
        if expires < time_now or token == None:
            self.perform_auth(self.get_access_code())
            return self.get_access_token()
        return token
# Queries #########################################################################################    
    
    def get_total_count(self):
        headers = {'Authorization': f'Bearer {self.get_access_token()}', 'Accept': 'application/vnd.allegro.public.v1+json'}
        r = requests.get(self.api_url + 'sale/offers', headers=headers)
        res = r.json()
        return res['totalCount']
    
    def get_all_offers(self):
        headers = {'Authorization': f'Bearer {self.get_access_token()}', 'Accept': 'application/vnd.allegro.public.v1+json'}
        all_offers = set()
        for x in range(self.get_total_count()//1000+1):
            payload = {'limit': 1000, 'offset':x*1000, 'publication.status': 'ACTIVE'}
            r = requests.get(self.api_url + 'sale/offers', params=payload, headers=headers)
            res = r.json()
            all_offers.update({(item['id'], item['name'], item['primaryImage']['url']) for item in res['offers']})
        return all_offers
    
    def get_all_offers_ids(self):
        headers = {'Authorization': f'Bearer {self.get_access_token()}', 'Accept': 'application/vnd.allegro.public.v1+json'}
        all_offers_ids = set()
        for x in range(self.get_total_count()//1000+1):
            payload = {'limit': 1000, 'offset':x*1000, 'publication.status': 'ACTIVE'}
            r = requests.get(self.api_url + 'sale/offers', params=payload, headers=headers)
            res = r.json()
            all_offers_ids.update({item['id'] for item in res['offers']})
        return all_offers_ids
    
    def get_offer_fields(self, offer_id):
        headers = {'Authorization': f'Bearer {self.get_access_token()}', 'Accept': 'application/vnd.allegro.public.v1+json'}
        r = requests.get(self.api_url + 'sale/offers/' + offer_id, headers=headers)
        res = r.json()
        try:
            if res['errors']: return 'error'
        except: pass
        id = res['id']
        name = res['name']
        slug = slugify.slugify(name)
        description = res['description']['sections'][0]['items'][0]['content']
        images = [x['url'] for x in res['images']]
        price = float(res['sellingMode']['price']['amount'])
        create_date = res['createdAt'].replace('T', ' ').replace('Z', '')
        offer = {'id': id, 'name': name, 'slug': slug, 'description': description, 'images': images, 'price': price, 'create_date': create_date}
        return offer

