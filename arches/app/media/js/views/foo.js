import { createApp } from 'vue';
import Index from 'Index.vue';

const app = createApp(Index);
app.provide('renderContext', 'editor');
app.mount('#foo');