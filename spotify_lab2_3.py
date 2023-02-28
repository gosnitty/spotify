'''
thiis module contains fuctions
'''
import base64
import os
import pycountry
import folium
from flask import Flask, render_template, request
from dotenv import load_dotenv
from requests import post, get
from geopy.geocoders import Nominatim

load_dotenv()

id_client = os.getenv('Client_ID')

secret = os.getenv('Client_SECRET')

def token():
    '''
    this function gets access token
    '''
    auth_code = f'{id_client}:{secret}'

    response = post('https://accounts.spotify.com/api/token',
        timeout = 10,
        data = {'grant_type': 'client_credentials'},
        headers = {'Authorization': f'Basic {base64.b64encode(auth_code.encode()).decode()}'})

    return response.json()['access_token']

def artist(name):
    '''
    this function gets artist id
    '''
    response = get('https://api.spotify.com/v1/search',
        timeout = 10,
        params = {
        'query': name,
        'type': 'artist'
    },
        headers={'Authorization': f'Bearer {token()}'})

    return (response.json().get('artists').get('items')[0])['id']

def songs(artist_id):
    '''
    this function gets top track id
    '''
    response = get(
        f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks',
        timeout = 10,
        params = {
        'query': artist_id,
        'market':'ES'
    },
    headers = {'Authorization': f'Bearer {token()}'})

    return (response.json().get('tracks')[0])['id']

def points(song_id):
    '''
    this function gets avaible markets of top track
    '''
    response = get(
        f'https://api.spotify.com/v1/tracks/{song_id}',
        timeout = 10,
        params = {
        'query': song_id,
    },
        headers = {'Authorization': f'Bearer {token()}'})
    return response.json()['available_markets']

def coordinates(available_points):
    '''
    this function gets coordinates of top track
    '''
    coorc = []
    geolocator = Nominatim(user_agent= 'spotify')
    for i in available_points:
        try:
            coordinate = pycountry.countries.get(alpha_2 = i)
            if coordinate:
                location = geolocator.geocode(coordinate.name, timeout =10)
                if location:
                    coorc.append([location, [location.latitude, location.longitude]])
        except RuntimeError:
            continue
    return coorc


def filling_map(coordinate):
    '''
    this function returns the map with points of top track
    '''
    films_map = folium.Map(width=800,
        height=600,)
    films_chossed = folium.FeatureGroup(name = 'avaible_markets')
    films_map = folium.Map(tiles='Stamen Toner',
                    zoom_start=1)
    for i, elem in enumerate(coordinate):
        films_chossed.add_child(folium.Marker(location = [coordinate[i][1][0],\
            coordinate[i][1][1]],
                                popup = coordinate[i][0],
                                icon=folium.Icon('red')))
    films_map.add_child(films_chossed)

    films_map.add_child(folium.LayerControl())
    films_map.save('templates/map.html')
    return films_map

app = Flask(__name__)

@app.route('/')
def index():
    '''
    html where you can put input
    '''
    return render_template('index.html')

@app.route("/", methods=('GET',"POST"))
def main():
    '''
    loads map to html
    '''
    if request.method == "POST":
        artist_name =  request.form.get('artist')
        created_map = filling_map(coordinates(points(songs(artist(artist_name)))))
        return render_template('map_song.html', map = created_map._repr_html_(),)


if __name__ == '__main__':
    app.run(debug = True)
