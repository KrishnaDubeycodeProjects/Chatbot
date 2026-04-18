import logging

logging.basicConfig(
    filename="backend/logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log(msg):
    logging.info(msg)