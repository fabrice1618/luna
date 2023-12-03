from sqlalchemy import create_engine, text
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, ForeignKey

from app_config import DATABASE_INTERFACE_URL

metadata_obj = MetaData()
engine = create_engine(DATABASE_INTERFACE_URL, echo=False)
