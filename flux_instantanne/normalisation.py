import logging
import json
from app_config import config_log
from flux_instantanne.rawdata import rawdata_generator

def transform_prix(prix_str):
    prix_in = json.loads(prix_str)
    if isinstance(prix_in, dict):
        prix_out = list()
        prix_out.append(prix_in)
    else:
        prix_out = prix_in

    return prix_out

def transform_coord(coord):
    if isinstance(coord, str):
        result = float(coord)
    else:
        result = coord
    return result / 100000

def transform_service(service):
    if isinstance(service, str):
        result = list()
        result.append(service)
    else:
        result = service
    return result

HORAIRES_DEFAULT = '{"@automate-24-24": "", "jour": []}'
SERVICES_DEFAULT = '{"service": []}'
PRIX_DEFAULT = '[]'

LEVEL1_FIELDS = {
    'id': {'type': "int"},
    'cp': {'type': "str"},
    'adresse': {'type': "str", 'reject_none': True},
    'ville': {'type': "str", 'reject_none': True},
    'pop': {'type': "str"},
    'departement': {'type': "str", 'reject_none': True},
    'code_departement': {'type': "str", 'reject_none': True},
    'region': {'type': "str", 'reject_none': True},
    'code_region': {'type': "str", 'reject_none': True},
    'services_service': {'type': "list", 'default': []},
    'services': {'type': "dict", 'transform': json.loads, 'default': SERVICES_DEFAULT},        
    'latitude': {'type': "float", 'transform': transform_coord},        
    'longitude': {'type': "float", 'transform': transform_coord},        
    'geom': {'type': "dict"},        
    'horaires': {'type': "dict", 'transform': json.loads, 'default': HORAIRES_DEFAULT},
    'horaires_automate_24_24': {'type': "str"},        
    'carburants_disponibles': {'type': "list", 'default': []},
    'carburants_indisponibles': {'type': "list", 'default': []},
    'gazole_maj': {'type': "str", 'default': ""},
    'gazole_prix': {'type': "float", 'transform': float, 'default': 0.0},
    'sp95_maj': {'type': "str", 'default': ""},
    'sp95_prix': {'type': "float", 'transform': float, 'default': 0.0},
    'e85_maj': {'type': "str", 'default': ""},
    'e85_prix': {'type': "float", 'transform': float, 'default': 0.0},
    'gplc_maj': {'type': "str", 'default': ""},
    'gplc_prix': {'type': "float", 'transform': float, 'default': 0.0},
    'e10_maj': {'type': "str", 'default': ""},
    'e10_prix': {'type': "float", 'transform': float, 'default': 0.0},
    'sp98_maj': {'type': "str", 'default': ""},
    'sp98_prix': {'type': "float", 'transform': float, 'default': 0.0},
    'prix': {'type': "list", 'transform': transform_prix, 'default': PRIX_DEFAULT},
}

GEOM_FIELDS = {
    'lat': {'type': "float"},
    'lon': {'type': "float"},
}

HORAIRES_FIELDS = {
    '@automate-24-24': {'type': "str"},
    'jour': {'type': "list"}
}

SERVICES_FIELDS = {
    'service': {'type': "list", 'transform': transform_service},
}
             

def normalize(result_data, reference_fields):
    fields1 = { x for x in reference_fields}
    fields2 = set(result_data.keys())

    champs_manquants = fields1 - fields2
    if len(champs_manquants) > 0:
        message_erreur = f"Champs manquants: {champs_manquants}"        
        logging.error(message_erreur)
        raise ValueError(message_erreur)

    champs_extra = fields2 - fields1
    if len(champs_extra) > 0:
        message_erreur = f"Champs en trop: {champs_extra}"        
        logging.error(message_erreur)
        raise ValueError(message_erreur)

    champs_ok = fields1 & fields2
    for champ in champs_ok:
        val = result_data[champ]
        reference = reference_fields[champ]
        
        if val is None:
            if 'reject_none' in reference and \
                reference['reject_none'] == True: 
                message_erreur = f"Erreur {champ} is None: {result_data}"
                logging.error(message_erreur)
                return False
            
            if not 'default' in reference or reference['default'] is None:
                message_erreur = f"Erreur {champ} is None: {result_data}"
                logging.error(message_erreur)
                raise ValueError(message_erreur)
            else:
                val = reference['default']

        transform_func = reference.get('transform')
        if transform_func is not None:
            val = transform_func(val)

        if str(type(val)) != f"<class '{reference['type']}'>":
            print(f"champ:{champ} {type(val)} valeur:", val)
            raise ValueError(f"Erreur Type: {str(type(val))}")

        result_data[champ] = val

    return True

def normalized_generator(limit = None):
    for idx, out_data in rawdata_generator():

        if not isinstance(out_data, dict):
            raise ValueError(f"Record {idx} type:{type(out_data)} Type incorrect. Value {out_data}")

        if limit is not None and idx == limit:
            return

        if normalize(out_data, LEVEL1_FIELDS) \
            and normalize(out_data['geom'], GEOM_FIELDS) \
            and normalize(out_data['horaires'], HORAIRES_FIELDS) \
            and normalize(out_data['services'], SERVICES_FIELDS):

            yield idx, out_data

    return


if __name__ == "__main__":
    config_log()
    for idx, normalized_station in normalized_generator():
        print(f"index={idx}, station={normalized_station}")
    