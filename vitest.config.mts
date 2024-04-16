import path from 'path';
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";


export default defineConfig({
    plugins: [vue()],
    test: {
        alias: {
            '@/': new URL(path.join(path.basename(__dirname), 'app', 'src', '/'), import.meta.url).pathname,
        },
        coverage: {
            include: [path.join(path.basename(__dirname), 'app', 'src', '/')],
            exclude: [
                '**/node_modules/**', 
                '**/dist/**', 
                '**/cypress/**', 
                '**/.{idea,git,cache,output,temp}/**', 
                '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*',
                path.join(path.basename(__dirname), 'install', '**')
            ],
            reporter: [
                ['clover', { 'file': 'coverage.xml' }],
                'text',
            ],
            reportsDirectory: path.join(__dirname, 'coverage', 'vue'),
        },
        environment: "jsdom",
        globals: true,
        exclude: [
            '**/node_modules/**', 
            '**/dist/**', 
            '**/cypress/**', 
            '**/.{idea,git,cache,output,temp}/**', 
            '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*',
            path.join(path.basename(__dirname), 'install', '**')
        ],
        setupFiles: ['vitest.setup.mts'],
    },
});
