from sqlalchemy import  text, Table, Column, Integer, String

from database_interface import metadata_obj, engine

SQL_SELECT_SERVICE = "SELECT service_id, service FROM services WHERE service = :service LIMIT 1"
SQL_INSERT_SERVICE = "INSERT INTO services(service) VALUES (:service)"

def create_table_services():
    services_table = Table(
        "services",
        metadata_obj,
        Column("service_id", Integer, primary_key=True, autoincrement=True),
        Column("service", String),
    )
    metadata_obj.create_all(engine, [services_table])


def service_read(service):
    with engine.connect() as conn:
        result = conn.execute(text(SQL_SELECT_SERVICE), {"service": service})
        return result.first()


def service_insert(service):
    with engine.connect() as conn:
        result = conn.execute(text(SQL_INSERT_SERVICE), {"service": service})
        conn.commit()

def services_convert(services):
    result = list()

    for service in services:
        serv = service_read(service)
        if serv is not None:
            result.append(serv.service_id)

    result.sort()
    return result

def main():
    pass

if __name__ == '__main__':
    main()