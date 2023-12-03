import logging

from app_config import config_log
from flux_instantanne.canonical import canonical_generator
from database_interface.departements import departement_filter, departement_read, departement_insert

def main():
    for _, station in canonical_generator():
        dep_data = departement_filter(station)
        reference = departement_read( dep_data["code_departement"] )

        if reference is None:
            departement_insert( dep_data )
            logging.info(f"Insertion département: {dep_data}")

        elif reference != dep_data:
            logging.warning(f"Modification département: {reference=} {dep_data=}")

if __name__ == '__main__':
    config_log()
    logging.info("Starting process: reference Departements")

    main()