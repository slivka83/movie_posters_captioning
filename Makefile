## Make Dataset

data/raw/films_set.pkl: data/external/imdb_db.csv data/external/kinopoisk.csv
	python3 src/data/make_dataset.py getUniqFilms

data/raw/kp_reponses.pkl: data/raw/films_set.pkl
	python3 src/data/make_dataset.py downloadFilmsDescription

data/interim/films_df.pkl: data/raw/kp_reponses.pkl
	python3 src/data/make_dataset.py parseFilmReponses

data/processed/films_df.pkl: data/interim/films_df.pkl
	python3 src/data/make_dataset.py filmsDescriptionPreproc

data/img: data/interim/films_df.pkl
	python3 src/data/make_dataset.py downloadImgs