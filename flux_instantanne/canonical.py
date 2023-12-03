import logging
import json
from datetime import datetime
from pytz import timezone
from flux_instantanne.normalisation import normalized_generator

FIELD_COPY = [ 'id', 'cp', 'adresse', 'ville', 'pop', 
              'departement', 'code_departement', 'region', 'code_region' ]

def get_geoloc(data):
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    geom = data.get('geom')

    if latitude != geom['lat'] or longitude != geom['lon']:
        message_erreur = f"Les valeurs de géolocalisation sont différentes: ({latitude},{longitude}) != ({geom['lat']},{geom['lon']})"
        logging.error(message_erreur)
        raise ValueError(message_erreur)

    return {'latitude': latitude, 'longitude': longitude}


def get_services(data):
    services1 = data.get('services_service')
    services2 = data['services']['service']

    services_set = set( services1 )
    services_set.update( services2 )

    return {'services': list(services_set)}


def translate_automate(value, conversion_table):

    if not value in conversion_table.keys():
        message_erreur = f"Valeurs horaires_automate_24_24 incorrecte: '{value}'"
        logging.error(message_erreur)
        raise ValueError(message_erreur)

    return conversion_table[value]


def get_automate_24_24(data):
    automate1 = data.get('horaires_automate_24_24')
    automate1_bool = translate_automate(automate1, {'Non': False, 'Oui': True})

    if not 'horaires' in data or data['horaires'] is None:
        automate2_bool = False    
    else:
        automate2 = data['horaires']['@automate-24-24']
        automate2_bool = translate_automate(automate2, {'': False, '1': True})

    if automate1_bool != automate2_bool:
        message_erreur = "Les valeurs automate_24_24 sont différentes"
        logging.error(message_erreur)
        raise ValueError(message_erreur)

    return {'automate_24_24': automate1_bool}


CARBURANTS = ['gazole', 'sp95', 'e85', 'gplc', 'e10', 'sp98']
CARBURANTS_CHAMPS = {'_maj': '', '_dispo': False, '_prix': 0.0}

def init_carburants():
    result = dict()

    for carburant in CARBURANTS:
        for key, val in CARBURANTS_CHAMPS.items():
            result[carburant + key] = val

    return result

def get_fromstr(datein):
    if datein == '':
        result = ''
    else:
        date_result = datetime.fromisoformat(datein)
        if date_result.tzinfo is None:
            date_result = date_result.replace(tzinfo=timezone('UTC'))

        result = date_result.isoformat()

    return result

def get_carburants_dict1(data):
    result = init_carburants()

    for carburant in CARBURANTS:
        field_maj = carburant + '_maj'
        field_prix = carburant + '_prix'

        result[field_maj] = get_fromstr( data[field_maj] )
        result[field_prix] = data[field_prix]

        if result[field_maj] != get_fromstr('') and result[field_prix] != 0:
            result[carburant + '_dispo'] = True

    return result


def get_carburants_dict2(data):
    result = init_carburants()

    carburants_indisponibles = [x.lower() for x in data['carburants_indisponibles']]
    for carburant in carburants_indisponibles:
        result[carburant + '_dispo'] = False

    carburants_disponibles = [x.lower() for x in data['carburants_disponibles']]
    for carburant in carburants_disponibles:
        result[carburant + '_dispo'] = True

    for prix in data['prix']:
        carburant = prix['@nom'].lower()

        result[carburant + '_maj'] = get_fromstr( prix['@maj'] )

        prix = float( prix['@valeur'] )
        result[carburant + '_prix'] = prix
        result[carburant + '_dispo'] = (prix != 0)

    return result

def dict_egaux(dict1, dict2):

    for cle, val1 in dict1.items():
        val2 = dict2[cle]
        if val1 != val2 and cle[-4:] != '_maj':
            return False

        if val1 != val2 and cle[-4:] == '_maj' and \
            datetime.fromisoformat(val1) != datetime.fromisoformat(val2):

            return False

    return True

def get_carburants(data):
    dict1 = get_carburants_dict1(data)
    dict2 = get_carburants_dict2(data)

    if not dict_egaux(dict1, dict2):
        message_erreur = f"valeurs de carburant différentes: station {data['id']}: {dict1} != {dict2}"
        logging.error(message_erreur)
        raise ValueError(message_erreur)
    
    return dict1


def print_station(data, indice=""):
    print(f"\n{'=' * 20} STATION {indice} {'=' * 20}")
    for key, val in data.items():
        if key in ['horaires', 'services']:
            val = json.dumps(val)
            val = val[:30] + "..."

        print(f"{key:16}: {val}")


def canonical_generator(limit = None):
    for idx, norm_pos in normalized_generator():

        if not isinstance(norm_pos, dict):
            message_erreur = f"Record {idx} type:{type(norm_pos)} Type incorrect. Value {norm_pos}"
            logging.error(message_erreur)
            raise ValueError(message_erreur)

        if limit is not None and idx == limit:
            return

        canoniq_pos = { champ: norm_pos[champ] for champ in FIELD_COPY }

        canoniq_pos.update(get_geoloc(norm_pos))
        canoniq_pos.update(get_services(norm_pos))
        canoniq_pos.update(get_automate_24_24(norm_pos))
        canoniq_pos.update({'horaires': norm_pos['horaires']['jour']})
        canoniq_pos.update(get_carburants(norm_pos))

        yield idx, canoniq_pos

    return