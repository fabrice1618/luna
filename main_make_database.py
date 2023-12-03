from database_interface.departements import create_table_departements
from database_interface.services import create_table_services
from database_interface.stations import create_table_stations
from database_interface.maj import create_table_maj

if __name__ == '__main__':
    create_table_departements()
    create_table_services()
    create_table_stations()
    create_table_maj()
