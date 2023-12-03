import json
from sqlalchemy import  text, Table, Column, Integer, String, Float, ForeignKey

from database_interface import metadata_obj, engine

CHAMPS_STATION = [ 
    "id", 
    "cp", 
    "adresse", 
    "ville", 
    "pop", 
    "code_departement", 
    "latitude", 
    "longitude", 
    "automate_24_24", 
    "horaires", 
    "services", 
    "gazole_maj", 
    "gazole_dispo", 
    "gazole_prix", 
    "sp95_maj", 
    "sp95_dispo", 
    "sp95_prix", 
    "e85_maj", 
    "e85_dispo", 
    "e85_prix", 
    "gplc_maj", 
    "gplc_dispo", 
    "gplc_prix", 
    "e10_maj", 
    "e10_dispo", 
    "e10_prix", 
    "sp98_maj", 
    "sp98_dispo", 
    "sp98_prix", 
]

SQL_SELECT_STATION = "SELECT * FROM stations WHERE id = :station_id LIMIT 1"
SQL_INSERT_STATION = """
    INSERT INTO stations(
        id, 
        cp, 
        adresse, 
        ville, 
        pop, 
        code_departement, 
        latitude, 
        longitude, 
        automate_24_24, 
        horaires, 
        services, 
        gazole_maj, 
        gazole_dispo, 
        gazole_prix, 
        sp95_maj, 
        sp95_dispo, 
        sp95_prix, 
        e85_maj, 
        e85_dispo, 
        e85_prix, 
        gplc_maj, 
        gplc_dispo, 
        gplc_prix, 
        e10_maj, 
        e10_dispo, 
        e10_prix, 
        sp98_maj, 
        sp98_dispo, 
        sp98_prix
    ) VALUES (
        :id, 
        :cp, 
        :adresse, 
        :ville, 
        :pop, 
        :code_departement, 
        :latitude, 
        :longitude, 
        :automate_24_24, 
        :horaires, 
        :services, 
        :gazole_maj, 
        :gazole_dispo, 
        :gazole_prix, 
        :sp95_maj, 
        :sp95_dispo, 
        :sp95_prix, 
        :e85_maj, 
        :e85_dispo, 
        :e85_prix, 
        :gplc_maj, 
        :gplc_dispo, 
        :gplc_prix, 
        :e10_maj, 
        :e10_dispo, 
        :e10_prix, 
        :sp98_maj, 
        :sp98_dispo, 
        :sp98_prix
    )
"""

def create_table_stations():
    stations_table = Table(
        "stations",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("cp", String, nullable=False),
        Column("adresse", String, nullable=False),
        Column("ville", String, nullable=False),
        Column("pop", String),
        Column("code_departement", ForeignKey("departements.code_departement"), nullable=False),
        Column("latitude", Float, nullable=False),
        Column("longitude", Float, nullable=False),
        Column("automate_24_24", Integer),
        Column("horaires", String),
        Column("services", String),
        Column("gazole_maj", String),
        Column("gazole_dispo", Integer),
        Column("gazole_prix", Float),
        Column("sp95_maj", String),
        Column("sp95_dispo", Integer),
        Column("sp95_prix", Float),
        Column("e85_maj", String),
        Column("e85_dispo", Integer),
        Column("e85_prix", Float),
        Column("gplc_maj", String),
        Column("gplc_dispo", Integer),
        Column("gplc_prix", Float),
        Column("e10_maj", String),
        Column("e10_dispo", Integer),
        Column("e10_prix", Float),
        Column("sp98_maj", String),
        Column("sp98_dispo", Integer),
        Column("sp98_prix", Float),
    )
    metadata_obj.create_all(engine, [stations_table])

def station_read(station_id):
    with engine.connect() as conn:
        result = conn.execute(text(SQL_SELECT_STATION), {"station_id": station_id})
        station_result = result.first()
        if station_result is None:
            return None

        station = station_result._asdict()
        station['horaires'] = json.loads(station['horaires'])
        station['services'] = json.loads(station['services'])

        return station

def station_insert(data):
    data['horaires'] = json.dumps(data['horaires'])
    data['services'] = json.dumps(data['services'])

    with engine.connect() as conn:
        result = conn.execute(text(SQL_INSERT_STATION), data)
        conn.commit()

def station_update(station_id, data):
    update_str = None
    for key in data:
        if update_str is None:
            update_str = ""
        else:
            update_str += ", "
        update_str += f"{key} = :{key} "

    requete = f"UPDATE stations SET {update_str} WHERE id = {station_id}"
    print(requete)
    raise RuntimeError("Not implemented")

def station_filter(data):
    result = { x: data[x] for x in CHAMPS_STATION }
    return result

def main():
    pass

if __name__ == '__main__':
    main()