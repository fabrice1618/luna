import json
from datetime import datetime
from sqlalchemy import  text, Table, Column, Integer, String, Float, ForeignKey

from database_interface import metadata_obj, engine

SQL_INSERT_MAJ = """
    INSERT INTO maj(
        timestamp, 
        operation, 
        station_id, 
        data
    ) VALUES (
        :timestamp, 
        :operation, 
        :station_id, 
        :data
    )
"""

def create_table_maj():
    maj_table =  Table(
        "maj",
        metadata_obj,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("timestamp", Integer, nullable=False, index=True),
        Column("operation", String, nullable=False),
        Column("station_id", Integer, nullable=False),
        Column("data", String, nullable=False),
    )
    metadata_obj.create_all(engine, [maj_table])


def maj_insert(operation, station_id, data):
    update_dict = {
        'timestamp': datetime.now().timestamp(),
        'operation': operation, 
        'station_id': station_id, 
        'data': json.dumps(data)
        }
    with engine.connect() as conn:
        result = conn.execute(text(SQL_INSERT_MAJ), update_dict)
        conn.commit()

def main():
    pass

if __name__ == '__main__':
    main()