import fs from 'fs';
import path from 'path';
import vue from "@vitejs/plugin-vue";

import { defineConfig } from 'vite';

import type { UserConfigExport } from 'vite';


function generateConfig(): Promise<UserConfigExport> {
    return new Promise((resolve, reject) => {
        const exclude = [
            '**/node_modules/**',
            '**/dist/**',
            '**/cypress/**',
            '**/.{idea,git,cache,output,temp}/**',
            '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*',
            path.join(path.basename(__dirname), 'install', '**')
        ];

        const rawData = fs.readFileSync(path.join(__dirname, '.frontend-configuration-settings.json'), 'utf-8');
        const parsedData = JSON.parse(rawData);

        const alias: { [key: string]: string } = {
            '@/arches': path.join(parsedData['ROOT_DIR'], 'app', 'src', 'arches'),
        };

        for (
            const [archesApplicationName, archesApplicationPath] 
            of Object.entries(
                parsedData['ARCHES_APPLICATIONS_PATHS'] as { [key: string]: string }
            )
        ) {
            alias[path.join('@', archesApplicationName)] = path.join(archesApplicationPath, 'src', archesApplicationName);
        }

        resolve({
            plugins: [vue()],
            test: {
                alias: alias,
                coverage: {
                    include: [path.join(path.basename(__dirname), 'src', '/')],
                    exclude: exclude,
                    reporter: [
                        ['clover', { 'file': 'coverage.xml' }],
                        'text',
                    ],
                    reportsDirectory: path.join(__dirname, 'coverage', 'frontend'),
                },
                environment: "jsdom",
                globals: true,
                exclude: exclude,
                passWithNoTests: true,
                setupFiles: ['vitest.setup.mts'],
            },
        });

    });
};

export default (async () => {
    const config = await generateConfig();
    return defineConfig(config);
})();