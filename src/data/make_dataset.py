# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd
import pickle
from tqdm.auto import tqdm
import urllib.request
import numpy as np
import seaborn as sns
from time import sleep
import click
import yaml


@click.group()
def cli():
    pass


@cli.command(name='getUniqFilms')
def get_uniq_films():
    kp = pd.read_csv('data/external/kinopoisk.csv',encoding='windows-1251')
    kp['NAME'] = kp['NAME'].replace(' +', ' ', regex=True)

    imdb = pd.read_csv('data/external/imdb_db.csv')

    films_set = list(set(list(kp['NAME'].dropna()) + list(imdb['NAME'].dropna())))
    print(f'Всего фильмов - {len(films_set)}')

    with open('data/raw/films_set.pkl', 'wb') as handle:
        pickle.dump(films_set, handle, protocol=pickle.HIGHEST_PROTOCOL)


@cli.command(name='downloadFilmsDescription')
def download_films_description():

    with open('config_private.yml') as f:
        config_private = yaml.safe_load(f)

    with open('data/raw/films_set.pkl', 'rb') as handle:
        films_set = pickle.load(handle)

    kp_reponses = {}

    for film_name in tqdm(enumerate(films_set)):    
        if film_name not in kp_reponses.keys():
            #print(film_name, end=' | ')
            
            url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={film_name}'
            headers = {
                'X-API-KEY': config_private['X-API-KEY'],
                'Content-Type': 'application/json',
            }
            r = requests.get(url, headers=headers)
            response = r.json()
            
            if 'status' in response.keys():
                break
            
            kp_reponses[film_name] = response

    with open('data/raw/kp_reponses.pkl', 'wb') as handle:
        pickle.dump(kp_reponses, handle, protocol=pickle.HIGHEST_PROTOCOL)


@cli.command(name='parseFilmReponses')
def parse_film_reponses():

    with open('data/raw/kp_reponses.pkl', 'rb') as handle:
        kp_reponses = pickle.load(handle)

    films_df = {}

    for film_name, response in tqdm(kp_reponses.items()):
        try:
            for f in response['films']:
                if 'description' in f.keys():
                    films_df[f['filmId']] = {
                        'filmId': f['filmId'],
                        'nameRu': f.get('nameRu', np.NaN),
                        'nameEn': f.get('nameEn', np.NaN),
                        'type': f['type'],
                        'year': f['year'],
                        'description': f['description'],
                        'countries': ','.join(sorted([v['country'] for v in f['countries']])),
                        'genres': ','.join(sorted([v['genre'] for v in f['genres']])),
                        'rating': f['rating'],
                        'posterUrl': f['posterUrl'],
                        'keyword': film_name
                    }
        except:
            print(f'Не удалось распарсить: {film_name}')    
                
    films_df = pd.DataFrame(films_df).T.reset_index(drop=True)

    films_df.to_pickle('data/interim/films_df.pkl')

@cli.command(name='filmsDescriptionPreproc')
def films_description_preproc():
    films_df = pd.read_pickle('data/interim/films_df.pkl')

    films_df_final = films_df
    films_df['description'] = (
        films_df['description']
        .str.replace('\xa0',' ')
        .str.replace('\u200b',' ')
        .str.replace('\n',' ', regex=False)
        .str.replace(r'\s+', ' ', regex=True))

    films_df.to_pickle('data/processed/films_df_final.pkl')

@cli.command(name='downloadImgs')
def download_imgs():
    films_df = pd.read_pickle('data/interim/films_df.pkl')

    for _, f in tqdm(films_df[['filmId','posterUrl']].iterrows(), total=films_df.shape[0]):
        f_path = f'data/img/{f["filmId"]}.jpg'
        if not os.path.isfile(f_path):
            urllib.request.urlretrieve(f['posterUrl'], f_path)


if __name__ == '__main__':
    cli()
