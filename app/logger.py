import json
import logging
import sys


# Formateur personnalisé qui convertit chaque log en JSON
# Avantage : les outils de monitoring (Grafana, Datadog...) peuvent parser ces logs facilement
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "level": record.levelname,       # ex: INFO, ERROR, WARNING
            "message": record.getMessage(),  # le message du log
            "module": record.module,         # le fichier source (ex: database)
        }
        # Ajoute les détails de l'exception si elle existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


# Fonction utilitaire à appeler dans chaque module de l'app
# Remplace le logging.getLogger() standard
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    # Evite d'ajouter plusieurs handlers si le logger est déjà configuré
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)  # affiche dans la console/Docker logs
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
