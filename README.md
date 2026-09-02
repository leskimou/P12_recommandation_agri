# Projet 12 Prédiction du rendement agricole

Prédit le rendement agricole (`Yield_tons_per_hectare`) à partir de données
sur la culture, la région, le sol et la météo. Le modèle (pipeline sklearn)
est entraîné dans les notebooks puis exposé via une API FastAPI + une app
Streamlit.

## Installation

```
uv sync
make install
```

## Lancer les notebooks

```
uv run jupyter lab
```

Ouvrir `analyse_exploratoire.ipynb` (exploration des données) ou
`modelisation.ipynb` (entraînement/évaluation du modèle).

## Lancer l'API et l'app

```
make api    # API FastAPI sur http://localhost:8000
make app    # App Streamlit
make run    # les deux en parallèle
```

Le modèle est téléchargé automatiquement depuis Hugging Face
(`leskimou/projet_12`) au démarrage de l'API.

## Tests

```
make test
```
