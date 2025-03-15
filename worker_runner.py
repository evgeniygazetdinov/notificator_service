import logging
from lib.queue.worker_runner import run_workers

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting workers...")
    run_workers()