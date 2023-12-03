# Projet Luna

## Description du système

### 0 - Architecture

```mermaid
    C4Deployment
    title Architecture du projet Luna

    Deployment_Node(navigateur, "Navigateur de l'utilisateur", "Firefox, Chrome, Edge, Safari"){
        Container(browser, "Site Mobile", "", "Fournir un fichier manifest.json")
    }
    Deployment_Node(serveur_VPS, "Serveur VPS", "Ubuntu 22.04 LTS + Docker"){
        Deployment_Node(dc_front, "docker_compose_front", ""){
            Container(api, "API Application", "Python3 + Flask", "/autocomplete /stations")
            Container(website, "Site web front", "Python3 + Flask", "HTML / CSS / JS / assets")
        }
        Deployment_Node(dc_db, "docker_compose_database", ""){
            ContainerDb(database, "Base de données", "Cassandra / Oracle / MySQL...", "Données actualisées des stations service")
        }
        Deployment_Node(dc_data, "docker_compose_datasource", ""){
            Container(data_update, "Data Update", "Python3 + SQLite3", "Traite les données sources + MAJ database")
        }
    }
    Deployment_Node(source_donnee, "Source de données du gouvernement", "https://data.economie.gouv.fr/api"){
        Container(datasource, "Fichier JSON", "", "prix-des-carburants-en-france-flux-instantane-v2")
    }

    Rel(browser, api, "Accès API", "JSON / HTTPS")
    Rel(browser, website, "", "HTML-CSS-JS")
    Rel(api, database, "", "")
    Rel(website, database, "", "")
    Rel_R(data_update, datasource, "read JSON")
    Rel(data_update, database, "Update database", "")

    UpdateRelStyle(browser, api, $offsetY="-80", $offsetX="-40")
    UpdateRelStyle(browser, website, $offsetX="-40", $offsetY="-20")
```

### 1 - Schéma du traitement de données de la source

Les étapes de traitement de données sont construites sous forme de générateurs.

- **rawdata_generator**: données brutes provenant de la source de données
- **normalized_generator**: données dans un format homogène, garantissant:
    - Tous les champs existent
    - Les champs obligatoires sont initialisés
    - les données sont dans le bon type de données
    - Les valeurs None sont intialisées
- **canonical_generator**: données contrôlées dans leur forme canonique, garantissant:
    - les données apparaissant dans 2 champs sont identiques
    - la structure des attributs est simplifiée

```mermaid
sequenceDiagram
    actor User as user
    participant canonic as Canonic data generator
    participant norm as Normalised data generator
    participant raw_data as Raw data generator
    participant cache as Cache
    actor Datasource

    User->>canonic: GET canonic data
    activate canonic
    canonic->>norm: GET normalized data
    activate norm
    norm->>raw_data: GET raw data
    activate raw_data
    alt JSON file not loaded
        raw_data->>cache: GET JSON file
        activate cache
        alt supérieur à CACHE_DELAY
            cache->>Datasource: request flux-instantane 
            activate Datasource
            Datasource->>cache: cache json data
            deactivate Datasource        
        end
    end
    
    cache->>raw_data: file flux_instantane.json
    deactivate cache

    loop generator
        raw_data->>norm: YIELD record
    end
    loop generator
        norm->>canonic: YIELD record
    end
    loop generator
        canonic->>User: YIELD record
    end
    deactivate canonic
    deactivate norm
    deactivate raw_data

```

### 2 - database interface

Fichier: db_interface.sqlite

```SQL
sqlite> .fullschema
CREATE TABLE departements (
	code_departement VARCHAR(2) NOT NULL, 
	departement VARCHAR(30), 
	code_region VARCHAR(2), 
	region VARCHAR(30), 
	PRIMARY KEY (code_departement)
);
CREATE TABLE services (
	service_id INTEGER NOT NULL, 
	service VARCHAR, 
	PRIMARY KEY (service_id)
);
CREATE TABLE stations (
	id INTEGER NOT NULL, 
	cp VARCHAR NOT NULL, 
	adresse VARCHAR NOT NULL, 
	ville VARCHAR NOT NULL, 
	pop VARCHAR, 
	code_departement VARCHAR(2) NOT NULL, 
	latitude FLOAT NOT NULL, 
	longitude FLOAT NOT NULL, 
	automate_24_24 INTEGER, 
	horaires VARCHAR, 
	services VARCHAR, 
	gazole_maj VARCHAR, 
	gazole_dispo INTEGER, 
	gazole_prix FLOAT, 
	sp95_maj VARCHAR, 
	sp95_dispo INTEGER, 
	sp95_prix FLOAT, 
	e85_maj VARCHAR, 
	e85_dispo INTEGER, 
	e85_prix FLOAT, 
	gplc_maj VARCHAR, 
	gplc_dispo INTEGER, 
	gplc_prix FLOAT, 
	e10_maj VARCHAR, 
	e10_dispo INTEGER, 
	e10_prix FLOAT, 
	sp98_maj VARCHAR, 
	sp98_dispo INTEGER, 
	sp98_prix FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(code_departement) REFERENCES departements (code_departement)
);
CREATE TABLE maj (
	id INTEGER NOT NULL, 
	timestamp INTEGER NOT NULL, 
	operation VARCHAR NOT NULL, 
	station_id INTEGER NOT NULL, 
	data VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_maj_timestamp ON maj (timestamp);
```

```mermaid
classDiagram
class departements
departements: PRIMARY KEY code_departement NOT NULL
departements: VARCHAR(2) code_departement
departements: VARCHAR(30) departement 
departements: VARCHAR(2) code_region
departements: VARCHAR(30) region


class services
services: PRIMARY KEY service_id NOT NULL
services: INTEGER service_id
services: VARCHAR service 


class stations
stations: PRIMARY KEY id NOT NULL
stations: FOREIGN KEY code_departement
stations: INTEGER id NOT NULL
stations: VARCHAR cp NOT NULL
stations: VARCHAR adresse NOT NULL
stations: VARCHAR ville NOT NULL
stations: VARCHAR pop
stations: VARCHAR(2) code_departement NOT NULL
stations: FLOAT latitude NOT NULL, 
stations: FLOAT longitude NOT NULL, 
stations: INTEGER automate_24_24
stations: VARCHAR horaires
stations: VARCHAR services
stations: VARCHAR gazole_maj
stations: INTEGER gazole_dispo
stations: FLOAT gazole_prix
stations: VARCHAR sp95_maj
stations: INTEGER sp95_dispo
stations: FLOAT sp95_prix
stations: VARCHAR e85_maj
stations: INTEGER e85_dispo
stations: FLOAT e85_prix
stations: VARCHAR gplc_maj
stations: INTEGER gplc_dispo
stations: FLOAT gplc_prix
stations: VARCHAR e10_maj
stations: INTEGER e10_dispo
stations: FLOAT e10_prix
stations: VARCHAR sp98_maj
stations: INTEGER sp98_dispo
stations: FLOAT sp98_prix

departements <|-- stations
services <|-- stations

class maj
maj: id INTEGER NOT NULL
maj: timestamp INTEGER NOT NULL
maj: operation VARCHAR NOT NULL
maj: station_id INTEGER NOT NULL
maj: data VARCHAR NOT NULL
maj: PRIMARY KEY (id)
maj: INDEX ix_maj_timestamp ON maj (timestamp)

stations <|-- maj

```
