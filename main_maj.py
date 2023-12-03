import logging

from app_config import config_log
from flux_instantanne.canonical import canonical_generator
from database_interface.maj import maj_insert
from database_interface.stations import station_insert, station_read, station_update, station_filter
from database_interface.services import services_convert


def main():
    for idx, canoniq_pos in canonical_generator():
        canoniq_pos['services'] = services_convert(canoniq_pos['services'])

        data = station_filter(canoniq_pos)

        station = station_read(data["id"])
        if station is None:
            station_insert(data)
            maj_insert("insert", data["id"], data)
            logging.info(f"INSERT id{data['id']} {data['cp']} {data['ville']}")

        elif station != data:
            data_update = {}
            for key, val in data.items():
                if station[key] != val:
                    data_update[key] = val

            station_update(data["id"], data_update)
            maj_insert("update", data["id"], data_update)
            logging.info(f"UPDATE id={data['id']} {data.keys()}")

if __name__ == '__main__':
    config_log()
    logging.info("Hello world - starting process...")

    main()