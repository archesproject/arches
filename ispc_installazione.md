####DIPENDENZE software per windows

postgres e postgis

yarn

nodejs

elastichserach

python

osgeo
    
step by step

   1 -  installare postgres e postgis tramite lo stack (https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
    
   2 -  quando vi chiede la password usate il nome postgres
    
   3 -  quando installate postgis fate creare il template (dovete spuntare la casella crea template postgis)
    
   4 -  installa node js e assicuratevi di aggiungerla alla variabile d'ambiente https://nodejs.org/  (installando nodejs si installerà anche python)
    
   5 -  installa yarn tramite riga di comando 
                                                
        npm install --global yarn
    
   6 -  scarica  elastichsearch da https://www.elastic.co/downloads/past-releases/elasticsearch-7-4-1
     dezzippalo in qualsiasi posizione tu voglia  vai in elasticsearch\bin e avvia elastichsearch.bat (avviandolo via terminale aggiungete la -d per farlo girare in background)
     
   7 - installa osgeoW4     https://trac.osgeo.org/osgeo4w/     se avete installato già qgis potete saltare questo passaggio
     
   8 - git clone https://github.com/CNR-DHILab/arches.git  (sentiti libero di usare githubDesktop se volete)
     
   9 - posizionati nella cartella di arches (roo principale) con il terminale
 
   10 - crea ambiente virtuale :  
   
        python -m venv ENV
    
   11 - attiva l'ambiente virtuale : 
   
        ENV\Scripts\activate.bat
    
   12 - upgrade pip :  
   
        python -m pip install --upgrade pip
    
   13 - Installa pacchetto python arches : 
   
        pip install arches
    
   14 - in dataspace/dataspace/settings_local.py cambiare se necessario le path per le librerie gdal (sono nella cartella bin/ di osgeoW4)
    
   15 - posizionati nella directory di progetto arches/dataspace e fail setup del db: 
   
        python manage.py setup_db
    
   16 - ora ripristina il pacchetto con i dati: 
   
        python manage.py packages -o load_package -s dataspace/pkg
   
   17 - installa le dipendenze js:  
   
        yarn install --manage-folder dataspace/media/packages
        
        yarn add three
        
        yarn add plotly.js-dist
    
   18 - avvia il servizio 
   
        python manage.py runserver
    
   ora se vai dal tuo browser in localhost:8000 vedrai il servizio. per loggarti username: admin password:admin
