import json
import urllib.request as urllib2
import random

api_key = '77c8c8e7797a4c0eb655c2a0c0eba9ed'
api_url = 'https://api.themoviedb.org/3/'


def get_json(url):
    '''Returns json text from a URL'''
    response = None
    try:
        response = urllib2.urlopen(url)
        json_text = response.read().decode(encoding='utf-8')
        return json.loads(json_text)
    finally:
        if response != None:
            response.close()


def get_trending(timeframe='week', media_type='movie', count=15):
    trending_url = api_url + \
        '%s/%s/%s?api_key=%s&language=en-US' % ('trending', media_type, timeframe, api_key)
    json = get_json(trending_url)
    base_img_url = 'https://image.tmdb.org/t/p/w500/'
    movies = []
    for movie in json['results']:
        temp = get_json('http://api.themoviedb.org/3/movie/%s/videos?api_key=%s' %
                        (int(movie['id']), api_key))
        url = temp['results']
        movie['video_url'] = []
        ct = 0
        for k in url:
            movie['video_url'].append(
                'https://www.youtube.com/embed/%s' % k["key"])
            ct += 1
            if(ct == 5):
                break
        movie['poster_path'] = base_img_url+str(movie['poster_path'])
        movies.append(movie)
        count -= 1
        if(count == 0):
            break
    return movies


def get_movie(mov_id):
    movie_url = api_url + \
        'movie/%s?api_key=%s' % (mov_id, api_key)
    base_img_url = 'https://image.tmdb.org/t/p/w500/'
    json = get_json(movie_url)
    json['poster_path'] = base_img_url+str(json['poster_path'])
    movie = json
    temp = get_json('http://api.themoviedb.org/3/movie/%s/videos?api_key=%s' %
                    (int(movie['id']), api_key))
    url = temp['results']
    movie['video_url'] = []
    count = 0
    for k in url:
        movie['video_url'].append(
            'https://www.youtube.com/embed/%s' % k["key"])
        count += 1
        if(count == 5):
            break
    return movie


def get_genre(genre_id):
    trending_url = api_url + 'discover/movie?api_key=%s&with_genre=%s' % (
        api_key, genre_id)
    json = get_json(trending_url)
    base_img_url = 'https://image.tmdb.org/t/p/w500/'
    movies = []
    for movie in json['results']:
        temp = get_json('http://api.themoviedb.org/3/movie/%s/videos?api_key=%s' %
                        (int(movie['id']), api_key))
        url = temp['results']
        movie['video_url'] = []
        count = 0
        for k in url:
            movie['video_url'].append(
                'https://www.youtube.com/embed/%s' % k["key"])
            count += 1
            if(count == 5):
                break
        movie['video_url'] = 'https://www.youtube.com/embed/%s' % get_json('http://api.themoviedb.org/3/movie/%s/videos?api_key=%s' % (
            int(movie['id']), api_key))['results']['key']
        movie['poster_path'] = base_img_url+str(movie['poster_path'])
        movies.append(movie)
    return movies


def search_movie(mov_name):
    movie_url = api_url +\
        'search/movie?api_key=%s&query=%s' % (api_key, mov_name)
    base_img_url = 'https://image.tmdb.org/t/p/w500/'
    json = get_json(movie_url)
    movies = []
    for movie in json['results']:
        temp = get_json('http://api.themoviedb.org/3/movie/%s/videos?api_key=%s' %
                        (int(movie['id']), api_key))
        url = temp['results']
        movie['video_url'] = []
        count = 0
        for k in url:
            movie['video_url'].append(
                'https://www.youtube.com/embed/%s' % k["key"])
            count += 1
            if(count == 5):
                break
        movie['poster_path'] = base_img_url+str(movie['poster_path'])
        movies.append(movie)
    return movies
