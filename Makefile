## Make Dataset

data/raw/films_set.pkl: data/external/imdb_db.csv data/external/kinopoisk.csv
	python3 src/data/make_dataset.py getUniqFilms