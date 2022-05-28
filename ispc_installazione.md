### DIPENDENZE software (Windows)
- Python
- PostgreSQL e PostGIS
- Elasticsearch
- GDAL (OSGeo)
  - Non hai bisogno di QGIS o GRASS
- Node.js

#### Step by step

1. Installare PostgreSQL e PostGIS
  - **Windows:** [usa EnterpriseDB installers][1] e tramite lo stack (incluso) per PostGIS  
  - **Mac:** [scarica l'app Postgres][2]  


2. Quando vi chiede la password usate il nome *postgres*


3. Quando installate PostGIS fate creare il template (dovete spuntare la casella crea template_postgis)
  - **Mac:**  
> 1. `sudo mkdir -p /etc/paths.d && echo /Applications/Postgres.app/Contents/Versions/latest/bin | sudo tee /etc/paths.d/postgresapp`  
>  - Chiudi la finestra Terminale e aprine una nuova per rendere effettive le modifiche.
> 2. Prova scrivere `which psql`  
> 3. `psql -U postgres -c "CREATE DATABASE template_postgis;"`  
> 4. `psql -U postgres -d template_postgis -c "CREATE EXTENSION postgis;"`  


4. [Installa Node.js][3] e assicuratevi di aggiungerla alla variabile d'ambiente (installando Node.js si installerà anche Python)


5. Installa Yarn tramite riga di comando
  - **Windows:** `npm install --global yarn`
  - **Mac:** se hai una versione maggiore di 16.10, fai `corepack enable`


6. [Scarica Elasticsearch][4]
  - Dezzippalo in qualsiasi posizione tu voglia
  - Vai in `elasticsearch\bin`
    - **Windows:** avvia `elasticsearch.bat`   
    - **Mac:** avvia `elasticsearch`  
  - Avviandolo via terminale aggiungete la `-d` per farlo girare in background  


7. Installa GDAL
  - **Windows:** [Installa OSGeoW4][5]
    - Se avete installato già QGIS potete saltare questo passaggio  
  - **Mac:** [Installa GDAL][6]  


8. Clona https://github.com/CNR-DHILab/arches.git
  - Sentiti libero di usare GitHub Desktop se volete


9. Posizionati nella cartella di *arches* (root principale) con il terminale.  
  - Crea e attiva l'ambiente virtuale:  
`python3 -m venv ENV`
    - **Windows:** `ENV\Scripts\activate.bat`  
    - **Mac:** `source ENV/bin/activate`  


11. Upgrade pip:  
`python3 -m pip3 install --upgrade pip`


12. Installa pacchetto python arches:  
`pip3 install arches`  


13. (Opzionale Windows) in *dataspace/dataspace/settings_local.py* cambiare se necessario le path per le librerie GDAL (sono nella cartella *bin/* di OSGeoW4)


14. Posizionati nella directory di progetto *arches/dataspace* e fa il setup del db:  
`python3 manage.py setup_db`


15. Ora ripristina il pacchetto con i dati:  
`python3 manage.py packages -o load_package -s dataspace/pkg`  


16. Posizionati nella directory di *arches/dataspace/dataspace/media*  
  - Devi avere 3 cartelli: *css/*, *img/*, e *js/*  
  - Installa le dipendenze js:
  > `yarn install --modules-folder ./packages`  
  > `yarn add three`  
  > `yarn add plotly.js-dist`

  - Ora devi vedere 4 cartelli.  


17. Avvia il servizio:  
`python3 manage.py runserver`


18. Ora se vai dal tuo browser in `localhost:8000`, vedrai il servizio. per loggarti
> username: `admin`  
> password: `admin`


[1]: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads  
[2]: https://postgresapp.com/downloads.html  
[3]: https://nodejs.org/  
[4]: https://www.elastic.co/downloads/past-releases/elasticsearch-7-17-3  
[5]: https://trac.osgeo.org/osgeo4w/  
[6]: https://gdal.org/download.html#current-release
