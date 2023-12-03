import logging

RAWDATA_URL = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/json?lang=fr&timezone=Europe%2FParis"
CACHE_FILE = "flux_instantane.json.bz2"
CACHE_DELAY = 100 * 60
LOG_FILE = 'myapp.log'
DATABASE_INTERFACE_URL = "sqlite+pysqlite:///db_interface.sqlite"

def config_log():
    """
    Configuration des logs
    """
    logging.basicConfig(
        filename=LOG_FILE, 
        level=logging.INFO, 
        format='%(levelname)s:%(asctime)s %(filename)s %(funcName)s - %(message)s', 
        datefmt='%d/%m/%Y %H:%M:%S'
        )

if __name__ == '__main__':
    config_log()