'''
thiis module contains fuctions
'''
import os
import base64
import pycountry
import folium
from dotenv import load_dotenv
from requests import post, get
from geopy.geocoders import Nominatim

load_dotenv()

CLIENT_ID = os.getenv('Client_ID')

CLIENT_SECRET = os.getenv('Client_SECRET')

def token():
    '''
    this function gets access token
    '''
    auth_code = f'{CLIENT_ID}:{CLIENT_SECRET}'

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

# print(coordinates(points(songs(artist('AC/DC')))))

def filling_map(coordinat):
    '''
    this function returns the map with points of top track
    '''
    films_map = folium.Map()
    films_chossed = folium.FeatureGroup(name = 'Artist')
    films_map = folium.Map(tiles="Stamen Terrain",
                    zoom_start=1)
    for i, elem in enumerate(coordinates):
        films_chossed.add_child(folium.Marker(location = [coordinat[i][1][0], coordinat[i][1][1]],
                                popup = coordinat[i][0],
                                icon=folium.Icon('purple')))
    films_map.add_child(films_chossed)

    films_map.add_child(folium.LayerControl())
    films_map.save("Artist_map.html")
    return films_map


def several_artists(id_art):
    '''
    this function returns info about artist
    '''
    response = get(
    f'https://api.spotify.com/v1/artists/{id_art}',
    timeout = 10,
    params = {
    'query': id}, 
    headers = {'Authorization': f'Bearer {token()}'})
    artis = response.json()
    option = [i for i in artis]
    print(option)
    key = input()
    if type(artis[key]) == dict:
        print([i for i in artis[key]])
        key1 = input()
        return artis[key][key1]
    else:
        return artis[key]
