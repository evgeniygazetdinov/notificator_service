import logging
from lib.queue.worker import run_workers

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting workers...")
    run_workers()