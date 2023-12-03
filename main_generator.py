import logging
from app_config import config_log
from flux_instantanne.canonical import canonical_generator, print_station

def main():
    config_log()
    logging.info("Hello world - starting process...")

    for idx, canoniq_pos in canonical_generator(10):
        print_station(canoniq_pos, idx)

if __name__ == "__main__":
    main()
    