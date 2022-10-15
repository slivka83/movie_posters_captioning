# -*- coding: utf-8 -*-
import os
import pickle
import urllib.request
from time import sleep
import requests
import pandas as pd
from tqdm.auto import tqdm
import numpy as np
import click
import yaml


@click.group()
def cli():
    pass


@cli.command(name='getUniqFilms')
def get_uniq_films():
    kp_df = pd.read_csv('data/external/kinopoisk.csv', encoding='windows-1251')
    kp_df['NAME'] = kp_df['NAME'].replace(' +', ' ', regex=True)

    imdb_df = pd.read_csv('data/external/imdb_db.csv')

    films_set = list(
        set(list(kp_df['NAME'].dropna()) + list(imdb_df['NAME'].dropna())))
    print(f'Всего фильмов - {len(films_set)}')

    with open('data/raw/films_set.pkl', 'wb') as handle:
        pickle.dump(films_set, handle, protocol=pickle.HIGHEST_PROTOCOL)


@cli.command(name='downloadFilmsDescription')
def download_films_description():

    with open('config_private.yml', encoding='utf-8') as config_private_file:
        config_private = yaml.safe_load(config_private_file)

    with open('data/raw/films_set.pkl', 'rb') as handle:
        films_set = pickle.load(handle)

    kp_reponses = {}

    for film_name in tqdm(enumerate(films_set)):
        if film_name not in kp_reponses.keys():

            url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={film_name}'
            headers = {
                'X-API-KEY': config_private['X-API-KEY'],
                'Content-Type': 'application/json'
            }

            request = requests.get(url, headers=headers, timeout=10)
            response = request.json()
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
            for film in response['films']:
                if 'description' in film.keys():
                    films_df[film['filmId']] = {
                        'filmId': film['filmId'],
                        'nameRu': film.get('nameRu', np.NaN),
                        'nameEn': film.get('nameEn', np.NaN),
                        'type': film['type'],
                        'year': film['year'],
                        'description': film['description'],
                        'countries': ','.join(sorted([v['country'] for v in film['countries']])),
                        'genres': ','.join(sorted([v['genre'] for v in film['genres']])),
                        'rating': film['rating'],
                        'posterUrl': film['posterUrl'],
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
    films_df_final['description'] = (
        films_df['description']
        .str.replace('\xa0', ' ')
        .str.replace('\u200b', ' ')
        .str.replace('\n', ' ', regex=False)
        .str.replace(r'\s+', ' ', regex=True))

    films_df.to_pickle('data/processed/films_df_final.pkl')


@cli.command(name='downloadImgs')
def download_imgs():
    films_df = pd.read_pickle('data/interim/films_df.pkl')

    for _, film in tqdm(films_df[['filmId', 'posterUrl']].iterrows(), total=films_df.shape[0]):
        f_path = f'data/img/{film["filmId"]}.jpg'
        if not os.path.isfile(f_path):
            urllib.request.urlretrieve(film['posterUrl'], f_path)


if __name__ == '__main__':
    cli()
