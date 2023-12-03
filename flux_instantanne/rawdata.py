import os
import time
import requests
import logging
from app_config import RAWDATA_URL, CACHE_FILE, CACHE_DELAY, config_log
import flux_instantanne.compress_json as compress_json

# Retourne True si aucun fichier récent n'est présent
def cache_miss():
    if not os.path.exists(CACHE_FILE):
        return True

    # Verification date modification du fichier
    file_age = time.time() - os.path.getmtime(CACHE_FILE)
    logging.info(f"File {CACHE_FILE} is {file_age} seconds old.")
    if file_age > CACHE_DELAY:
        os.remove(CACHE_FILE)
        return True

    return False


def request_rawdata():
    logging.info(f"Requesting data URL={RAWDATA_URL[:70]}...")

    response = requests.get(RAWDATA_URL)
    if response.status_code != 200:
        message_erreur = f"Erreur lors de la requête : {response.status_code} - {response.text}"
        logging.error(message_erreur)
        raise RuntimeError(message_erreur)

    rawdata = response.json()
    if not isinstance(rawdata, list):
        message_erreur = f"Erreur type attendu list, recu={type(rawdata)}"
        logging.error(message_erreur)
        raise ValueError(message_erreur)

    return rawdata

def load_rawdata():
    if cache_miss():
        # Faire la requete sur le site
        rawdata = request_rawdata()

        # Save rawdata
        compress_json.dump(rawdata, CACHE_FILE)
        logging.info(f"Saved JSON rawdata {CACHE_FILE}, {len(rawdata)} records")

    else:
        # Charger à partir du cache
        rawdata = compress_json.load(CACHE_FILE)
        logging.info(f"Loaded JSON {CACHE_FILE}, {len(rawdata)} records")

    # Vérifier que des données sont bien chargées
    if rawdata is None:
        message_erreur = f"Error load_rawdata: rawdata is None"
        logging.error(message_erreur)
        raise RuntimeError(message_erreur)

    return rawdata

def rawdata_generator(limit = None):
    """
    Générateur de rawdata
    """
    rawdata_store = load_rawdata()

    logging.info(f"Starting generator with {len(rawdata_store)} records")
    for idx, rawdata_station in enumerate(rawdata_store):
        if not isinstance(rawdata_station, dict):
            message_erreur = f"Error record:{idx} type:{type(rawdata_station)} should be <class 'dict'>"
            logging.error(message_erreur)
            raise ValueError(message_erreur)
        
        if limit is not None and idx == limit:
            return
        
        yield idx, rawdata_station


# Programme principal
if __name__ == '__main__':
    config_log()
    for idx, rawdata_station in rawdata_generator(5):
        print(f"index={idx}, station={rawdata_station}")

