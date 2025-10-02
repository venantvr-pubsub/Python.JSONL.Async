import json
import os
import threading

import pytest

from python_jsonl_async import AsyncJsonlQueue


## Fixtures (inchangées)
# noinspection PyProtectedMember
@pytest.fixture
def manager(tmp_path):
    file_path = tmp_path / "test_events.jsonl"
    instance = AsyncJsonlQueue(str(file_path))
    instance.start()
    assert instance.wait_for_ready(timeout=5), "Le worker n'a pas démarré à temps"
    yield instance, str(file_path)
    if instance._worker and instance._worker.is_alive():
        instance.stop()


## Tests (inchangés sauf le dernier)
def test_initialization(tmp_path):
    file_path = tmp_path / "init.jsonl"
    instance = AsyncJsonlQueue(str(file_path))
    assert instance.file_path == str(file_path)
    assert instance._worker is None


def test_lifecycle_start_stop(manager):
    instance, _ = manager
    assert instance._worker is not None and instance._worker.is_alive()
    worker_thread = instance._worker
    instance.stop()
    assert not worker_thread.is_alive()
    assert instance._worker is None


def test_single_write_operation(manager):
    instance, file_path = manager
    test_data = {"event_id": 1, "message": "hello world"}
    instance.write(test_data)
    instance.stop()
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        line = f.readline()
        read_data = json.loads(line)
    assert read_data == test_data


def test_concurrent_writes(manager):
    instance, file_path = manager
    num_threads = 10
    writes_per_thread = 50
    total_writes = num_threads * writes_per_thread
    threads = []

    def writer_task(thread_id):
        # noinspection PyShadowingNames
        for i in range(writes_per_thread):
            instance.write({"thread_id": thread_id, "iteration": i})

    for i in range(num_threads):
        thread = threading.Thread(target=writer_task, args=(i,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    instance.stop(timeout=10)
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    assert len(lines) == total_writes


## Test du Gestionnaire de Contexte (CORRIGÉ)
def test_context_manager_usage(tmp_path):
    """
    Vérifie que la librairie fonctionne correctement avec un bloc 'with'.
    Le test se concentre sur le résultat final : le fichier est bien écrit.
    """
    file_path = tmp_path / "context_test.jsonl"
    test_data = {"context": "success"}

    with AsyncJsonlQueue(str(file_path)) as instance:
        instance.write(test_data)
        # À la sortie de ce bloc, __exit__ (et donc stop()) est appelé automatiquement.

    # On vérifie que la donnée a bien été écrite dans le fichier.
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        line = f.readline()
        read_data = json.loads(line)

    assert read_data == test_data
