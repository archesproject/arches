import { defineAsyncComponent } from 'vue';
import createVueApplication from 'utils/create-vue-application';

import pluginData from 'views/plugin-data';

// workaround for webpack failures surrounding dynamic imports
const vuePluginPath = pluginData['component'].replace('src/', '').replace('.vue', '');
const AsyncComponent = defineAsyncComponent(() => import(`@/${vuePluginPath}.vue`));

const pluginMountingPoint = document.querySelector('#plugin-mounting-point');
pluginMountingPoint.setAttribute("id", pluginData['slug']);

createVueApplication(AsyncComponent).then(vueApp => {
    vueApp.mount(`#${pluginData['slug']}`);
});
