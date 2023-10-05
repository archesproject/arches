import { createApp } from 'vue';
import Foo from 'Foo.vue';

const app = createApp(Foo);
app.provide('renderContext', 'editor');
app.mount('#foo');