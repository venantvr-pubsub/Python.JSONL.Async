import json
import logging
import os
import threading
import time
from collections import deque
from typing import Deque, Optional, Dict, Any

__all__ = ["AsyncJsonlQueue"]
logger = logging.getLogger(__name__)


class _JsonlWorker(threading.Thread):

    def __init__(
            self,
            file_path: str,
            write_queue: Deque,
            stop_event: threading.Event,
            ready_event: threading.Event
    ) -> None:
        super().__init__(name="AsyncJsonlQueueWorker")
        self.file_path = file_path
        self._write_queue = write_queue
        self._stop_event = stop_event
        self._ready_event = ready_event
        self.daemon = True
        self.file_handle = None

    def run(self) -> None:
        try:
            dir_name = os.path.dirname(self.file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            self.file_handle = open(self.file_path, 'a', encoding='utf-8')
            self._ready_event.set()

            # La boucle continue tant que le sentinel `None` n'est pas trouvé
            while True:
                try:
                    log_item = self._write_queue.popleft()
                    if log_item is None:
                        break  # Signal d'arrêt propre

                    json_line = json.dumps(log_item, ensure_ascii=False)
                    self.file_handle.write(json_line + '\n')
                    self.file_handle.flush()
                except IndexError:
                    # Si la file est vide et que l'event stop est levé, on sort
                    if self._stop_event.is_set():
                        break
                    time.sleep(0.01)
        finally:
            if self.file_handle:
                self.file_handle.close()


class AsyncJsonlQueue:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._write_queue: Deque[Optional[Dict[str, Any]]] = deque()
        self._queue_lock = threading.Lock()
        self._stop_worker_event = threading.Event()
        self._worker_ready_event = threading.Event()
        self._worker: Optional[_JsonlWorker] = None

    def start(self) -> None:
        if self._worker is not None and self._worker.is_alive():
            logger.warning("Le worker est déjà en cours d'exécution.")
            return
        logger.info(f"Démarrage du worker pour le fichier '{self.file_path}'...")
        self._stop_worker_event.clear()
        self._worker = _JsonlWorker(
            self.file_path, self._write_queue, self._stop_worker_event, self._worker_ready_event,
        )
        self._worker.start()

    def wait_for_ready(self, timeout: float = 10.0) -> bool:
        return self._worker_ready_event.wait(timeout=timeout)

    def stop(self, timeout: float = 5.0) -> None:
        if self._worker is None or not self._worker.is_alive():
            return
        logger.info("Arrêt du worker JSONL en cours...")

        # On attend que la file se vide avant d'envoyer le signal d'arrêt
        while len(self._write_queue) > 0:
            time.sleep(0.01)

        # Ajoute le signal d'arrêt (sentinel) à la file
        with self._queue_lock:
            self._write_queue.append(None)

        # L'événement est maintenant utilisé pour débloquer le worker s'il attend sur une file vide
        self._stop_worker_event.set()
        self._worker.join(timeout=timeout)

        if self._worker.is_alive():
            logger.error("Le worker n'a pas pu s'arrêter dans le temps imparti.")

        self._worker = None
        logger.info("Worker arrêté.")

    def write(self, data: Dict[str, Any]) -> None:
        with self._queue_lock:
            self._write_queue.append(data)

    def __enter__(self):
        self.start()
        self.wait_for_ready()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
