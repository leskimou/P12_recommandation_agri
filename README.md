# Projet 12 Prédiction du rendement agricole

Prédit le rendement agricole (`Yield_tons_per_hectare`) à partir de données
sur la culture, la région, le sol et la météo. Le modèle (pipeline sklearn)
est entraîné dans les notebooks puis exposé via une API FastAPI + une app
Streamlit.

**Interface en ligne :** https://leskimou-p12-recommandation-agri-apiapp-ldh3tb.streamlit.app/
(peut afficher un écran de réveil ou prendre 30-60s au premier appel après
une période d'inactivité, voir [Déploiement](#déploiement-docker-hub---render---streamlit-cloud)).

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

## Authentification de l'API

Les endpoints `/predict` et `/recommend` exigent une cle API envoyee dans le
header `X-API-Key`. `/health` reste public (utilise par le `HEALTHCHECK`
Docker et les smoke-tests CI).

La cle est lue depuis la variable d'environnement `API_KEY` (voir
`API/main.py`). Si elle n'est pas definie, l'authentification est
desactivee (pratique en local) : `curl -X POST .../predict ...` fonctionne
sans header. En production, il faut definir `API_KEY` pour proteger l'API.

## Deploiement (Docker Hub -> Render -> Streamlit Cloud)

```
GitHub (push sur master)
   |
   |  .github/workflows/api-ci-cd.yml
   v
Docker Hub  --------------------------->  Render (conteneur API)
leskimou/p12_recommandation_api:latest    https://<service>.onrender.com
                                                     ^
                                                     | API_URL + API_KEY (secrets)
                                                     |
                                           Streamlit Cloud (interface)
                                           https://<app>.streamlit.app
```

- **GitHub Actions** (`api-ci-cd.yml`) : a chaque push sur `master` touchant
  `API/**`, lance les tests, build l'image, puis la pousse sur Docker Hub
  (secrets repo `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` requis).
- **Docker Hub** (`leskimou/p12_recommandation_api`) : stocke l'image, ne
  l'execute pas.
- **Render** (free web service) : deploye l'image depuis Docker Hub
  ("Deploy an existing image from a registry"), variable d'env `API_KEY`
  a definir dans Render, port `8000`. Se met en veille apres inactivite
  (cold start ~30-60s au reveil, temps de retelecharger le modele HF). Un
  nouveau push sur Docker Hub n'est pas repull automatiquement, sauf
  Auto-Deploy active ou "Manual Deploy" declenche a la main.
- **Streamlit Cloud** (`API/app.py`) : interface publique qui appelle
  l'API. Secrets a definir dans Settings > Secrets, **a la racine** du
  TOML (pas dans une section) pour qu'ils soient aussi lus via
  `os.environ` :

  ```toml
  API_URL = "https://<service>.onrender.com"
  API_KEY = "<meme cle que sur Render>"
  ```

  La cle API n'est jamais exposee aux visiteurs de l'app : elle reste
  cote serveur Streamlit, qui l'ajoute au header `X-API-Key` de chaque
  appel a l'API.
