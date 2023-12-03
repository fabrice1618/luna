import logging

from app_config import config_log
from flux_instantanne.canonical import canonical_generator
from database_interface.services import service_read, service_insert

def main():
    for _, data in canonical_generator():
        
        for service in data['services']:
            serv = service_read(service)
            if serv is None:
                service_insert(service)
                serv = service_read(service)
                logging.info(f"Ajout service: ({serv.service_id}, {serv.service})")


if __name__ == '__main__':
    config_log()
    logging.info("Starting process: reference Services")

    main()    