import { createApp } from 'vue';
import Index from 'Index.vue';
import PrimeVue from 'primevue/config';

const app = createApp(Index);

app.use(PrimeVue);
app.mount('#foo');