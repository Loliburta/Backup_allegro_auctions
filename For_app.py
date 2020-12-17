import requests
import datetime


class AllegroAPI():
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    api_url = 'https://api.allegro.pl/'
    auth_url = "https://allegro.pl/auth/oauth/token?grant_type=client_credentials"
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        
    def perform_auth(self):
        auth_url = self.auth_url
        client_id = self.client_id
        client_secret = self.client_secret
        
        token_result = requests.post(auth_url, auth=(client_id, client_secret))
        result_code = token_result.status_code

        if result_code not in (200, 299):
            print("something went wrong")
            raise Exception("Could not authenticate client")
        
        token_object = token_result.json()
        time_now = datetime.datetime.now() 
        token_expires_in = token_object['expires_in']
        expires = time_now + datetime.timedelta(seconds=token_expires_in)
        
        self.access_token = token_object['access_token']
        self.access_token_expires = expires
        self.access_token_did_expire = expires < time_now
        return True
    
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        time_now = datetime.datetime.now()
        if expires < time_now or token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

# print(client.get_access_token())