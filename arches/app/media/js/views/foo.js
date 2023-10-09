import { createApp } from 'vue';
import Index from 'Index.vue';
import PrimeVue from 'primevue/config';
import { createGettext } from "vue3-gettext";
import translations from "templates/locale/translations.json";


window.fetch("api/userlang")
    .then(function(response){
        return response.json();
    })
    .then(function(response){
        console.log(response);
    
        const gettext = createGettext({
            availableLanguages: {
                en: "English",
                de: "Deutsch",
            },
            defaultLanguage: response.lang,
            translations: translations,
        });
        
        const app = createApp(Index);
        app.use(PrimeVue);
        app.use(gettext);
        app.mount('#foo');
    });
