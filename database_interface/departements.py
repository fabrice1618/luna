from sqlalchemy import text, Table, Column, String

from database_interface import metadata_obj, engine

CHAMPS_DEPARTEMENT = [ "code_departement", "departement", "code_region", "region",]

SQL_SELECT_DEPARTEMENT = "SELECT code_departement, departement, code_region, region FROM departements WHERE code_departement = :code_departement LIMIT 1"
SQL_INSERT_DEPARTEMENT = "INSERT INTO departements(code_departement, departement, code_region, region) VALUES (:code_departement, :departement, :code_region, :region)"


def create_table_departements():
    departements_table = Table(
        "departements",
        metadata_obj,
        Column("code_departement", String(2), primary_key=True),
        Column("departement", String(30)),
        Column("code_region", String(2)),
        Column("region", String(30)),
    )
    metadata_obj.create_all(engine, [departements_table])


def departement_read(code_departement):
    with engine.connect() as conn:
        result = conn.execute(
            text(SQL_SELECT_DEPARTEMENT), 
            {"code_departement": code_departement}
            )
        row = result.first()
        return row._asdict() if row is not None else None


def departement_insert(data):
    with engine.connect() as conn:
        result = conn.execute(
            text(SQL_INSERT_DEPARTEMENT), 
            data
            )
        conn.commit()


def departement_filter(data):
    return { x: data[x] for x in CHAMPS_DEPARTEMENT }


def main():
    pass

if __name__ == '__main__':
    main()