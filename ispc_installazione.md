### DIPENDENZE software (Windows)
- Python
- PostgreSQL e PostGIS
- Elasticsearch
- GDAL (OSGeo)
 - Non hai bisogno di QGIS o GRASS
- Devi avere Node.js

#### Step by step

1. Installare PostgreSQL e PostGIS
  - Windows: [Usa EnterpriseDB installers](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) e tramite lo stack (incluso) per PostGIS  
  - Mac: scarica l'app [Postgres](https://postgresapp.com/downloads.html)


2. Quando vi chiede la password usate il nome postgres


3. Quando installate PostGIS fate creare il template (dovete spuntare la casella crea template_postgis)
  - Mac:
> 1. `sudo mkdir -p /etc/paths.d && echo /Applications/Postgres.app/Contents/Versions/latest/bin | sudo tee /etc/paths.d/postgresapp`  
>  - Chiudi la finestra Terminale e aprine una nuova per rendere effettive le modifiche.
> 2. Prova scrivere `psql postgres`  
> 3. \# `create database template_postgis;`  

4. Installa [Node.js](https://nodejs.org/) e assicuratevi di aggiungerla alla variabile d'ambiente (installando Node.js si installerà anche Python)


5. Installa Yarn tramite riga di comando
  - Windows: `npm install --global yarn`
  - Mac: Se hai una versione maggiore di 16.10, fai `corepack enable`


6. Scarica [Elasticsearch](https://www.elastic.co/downloads/past-releases/elasticsearch-7-17-3) da https://www.elastic.co/downloads/past-releases/elasticsearch-7-4-1  
    - (Scegli MACOSX X86_64 se hai Intel, altrimenti con M1 Silicon scegli MACOSX_AARCH64)  
  - Dezzippalo in qualsiasi posizione tu voglia  
  - Vai in `elasticsearch\bin`  
    - Windows: Avvia `elasticsearch.bat`  
    - Mac: Avvia `elasticsearch`  
  - Avviandolo via terminale aggiungete la `-d` per farlo girare in background  
  
  
7. Installa GDAL
  - Windows: Installa [OSGeoW4](https://trac.osgeo.org/osgeo4w/)
    - Se avete installato già QGIS potete saltare questo passaggio
  - Mac: [Installa GDAL](https://gdal.org/download.html#current-release)


8. Clona https://github.com/CNR-DHILab/arches.git
  - Sentiti libero di usare GitHub Desktop se volete


9. Posizionati nella cartella di arches (root principale) con il terminale


10. Crea e attiva l'ambiente virtuale:  
`python3 -m venv ENV`
  - Windows: `ENV\Scripts\activate.bat`
  - Mac: `source ENV/bin/activate`


11. Upgrade pip:  
`python3 -m pip install --upgrade pip`


12. Installa pacchetto python arches:  
`pip install arches`


13. (Opzionale) in *dataspace/dataspace/settings_local.py* cambiare se necessario le path per le librerie GDAL (sono nella cartella *bin/* di OSGeoW4)


14. Posizionati nella directory di progetto *arches/dataspace* e fa il setup del db:  
`python3 manage.py setup_db`


15. Ora ripristina il pacchetto con i dati:  
`python manage.py packages -o load_package -s dataspace/pkg`  
- Se è la prima volta, puoi fare  
`python3 manage.py packages -o load_package -s dataspace/pkg -db -y`


16. Installa le dipendenze js:
> `yarn install --manage-folder arches/dataspace/media/packages`  
> `yarn add three`  
> `yarn add plotly.js-dist`


17. avvia il servizio  
`python manage.py runserver`


18. Ora se vai dal tuo browser in `localhost:8000`, vedrai il servizio. per loggarti
> username: `admin`  
> password: `admin`
