import logging
import os
import sys
from daphne.cli import CommandLineInterface

import os
import sys
from daphne.cli import CommandLineInterface

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CantinaShop.settings")

    sys.argv = [
        "daphne",
        "-b", "127.0.0.1",
        "-p", "8000",
        "CantinaShop.asgi:application",
    ]

    CommandLineInterface.entrypoint()
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Daphne server on port 8000")
