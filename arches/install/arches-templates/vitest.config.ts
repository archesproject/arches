import path  from 'path';
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";


export default defineConfig({
   plugins: [vue()],
   test: {
       alias: {
           '@/': new URL(path.join(path.basename(__dirname), 'src', '/'), import.meta.url).pathname,
       },
       coverage: {
           include: [path.join(path.basename(__dirname), 'src', '/')],
           reporter: [
               ['clover', { 'file': 'coverage.xml' }],
               'text',
           ],
           reportsDirectory: path.join(__dirname, 'coverage', 'vue'),
         },
       environment: "jsdom",
       globals: true,
       setupFiles: ['vitest.setup.ts'],
   },
});
