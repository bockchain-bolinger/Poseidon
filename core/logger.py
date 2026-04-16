import logging
import os
from pathlib import Path

# Basisverzeichnis ermitteln (Poseidon-Hauptordner)
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

class PoseidonLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PoseidonLogger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        self.logger = logging.getLogger("Poseidon")
        self.logger.setLevel(logging.DEBUG)
        
        # File Handler (für alle Logs)
        fh = logging.FileHandler(LOG_DIR / "poseidon.log", encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Console Handler (nur für Warnungen/Fehler in der Entwicklung, falls gewünscht)
        # ch = logging.StreamHandler()
        # ch.setLevel(logging.WARNING)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
        fh.setFormatter(formatter)
        # ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        # self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger

# Globaler Logger für einfachen Import
logger = PoseidonLogger().get_logger()
