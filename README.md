# Async JSONL Queue

[![PyPI version](https://badge.fury.io/py/python-jsonl-queue.svg)](https://badge.fury.io/py/python-jsonl-queue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Une librairie Python simple et robuste pour écrire dans des fichiers JSON Lines (.jsonl) de manière thread-safe, en déportant toutes les opérations d'écriture dans un
thread dédié pour ne pas bloquer votre application principale.

## Caractéristiques

- **Thread-safe** : Écritures concurrentes sécurisées depuis plusieurs threads
- **Non-bloquant** : Les opérations d'écriture sont asynchrones via une file d'attente
- **Simple d'utilisation** : API minimaliste avec support du context manager
- **Fiable** : Arrêt propre garantissant l'écriture de toutes les données en attente
- **Aucune dépendance externe** : Uniquement la bibliothèque standard Python

## Installation

```bash
pip install python-jsonl-queue
```

## Utilisation

### Exemple basique

```python
from async_jsonl_queue import AsyncJsonlQueue

# Créer et démarrer la queue
queue = AsyncJsonlQueue("output.jsonl")
queue.start()
queue.wait_for_ready()

# Écrire des données
queue.write({"event": "user_login", "user_id": 123})
queue.write({"event": "page_view", "page": "/home"})

# Arrêter proprement (écrit toutes les données en attente)
queue.stop()
```

### Avec context manager (recommandé)

```python
from async_jsonl_queue import AsyncJsonlQueue

with AsyncJsonlQueue("output.jsonl") as queue:
    queue.write({"event": "user_login", "user_id": 123})
    queue.write({"event": "page_view", "page": "/home"})
# L'arrêt propre est automatique
```

### Utilisation avec plusieurs threads

```python
import threading
from async_jsonl_queue import AsyncJsonlQueue


def worker(queue, thread_id):
    for i in range(100):
        queue.write({"thread_id": thread_id, "iteration": i})


with AsyncJsonlQueue("concurrent.jsonl") as queue:
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(queue, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
```

## API

### `AsyncJsonlQueue(file_path: str)`

Crée une nouvelle instance de la queue JSONL.

- **file_path** : Chemin du fichier JSONL à créer/compléter

### Méthodes

#### `start() -> None`

Démarre le thread worker d'écriture.

#### `wait_for_ready(timeout: float = 10.0) -> bool`

Attend que le worker soit prêt (fichier ouvert).

- **timeout** : Temps d'attente maximum en secondes
- **Retourne** : `True` si le worker est prêt, `False` en cas de timeout

#### `write(data: Dict[str, Any]) -> None`

Ajoute des données à la file d'écriture.

- **data** : Dictionnaire à écrire au format JSON Lines

#### `stop(timeout: float = 5.0) -> None`

Arrête proprement le worker après avoir écrit toutes les données en attente.

- **timeout** : Temps d'attente maximum en secondes

### Context Manager

La classe supporte le protocole de context manager (`with` statement) qui appelle automatiquement `start()`, `wait_for_ready()` à l'entrée et `stop()` à la sortie.

## Format JSONL

Le format JSON Lines (.jsonl) stocke un objet JSON par ligne :

```jsonl
{"event": "user_login", "user_id": 123}
{"event": "page_view", "page": "/home"}
{"event": "user_logout", "user_id": 123}
```

Ce format est idéal pour :

- Les logs structurés
- Les événements d'application
- Les flux de données à traiter ligne par ligne
- Les datasets d'apprentissage automatique

## Tests

```bash
# Installer les dépendances de développement
pip install -e ".[dev]"

# Exécuter les tests
pytest
```

## Licence

MIT License - voir le fichier LICENSE pour plus de détails.

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request sur [GitHub](https://github.com/venantvr-pubsub/Python.JSONL.Async).

## Auteur

venantvr - [venantvr@gmail.com](mailto:venantvr@gmail.com)