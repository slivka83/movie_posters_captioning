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


@click.group()
def cli():
    pass

@cli.command(name='getUniqFilms')
def get_uniq_films():
    kp = pd.read_csv('data/external/kinopoisk.csv',encoding='windows-1251')
    kp['NAME'] = kp['NAME'].replace(' +', ' ', regex=True)

    imdb = pd.read_csv('data/external/imdb_db.csv')

    films_set = list(set(list(kp['NAME'].dropna()) + list(imdb['NAME'].dropna())))

    with open('data/raw/films_set.pkl', 'wb') as handle:
        pickle.dump(films_set, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    cli()
