import fs from 'fs';
import path from 'path';
import vue from "@vitejs/plugin-vue";

import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { defineConfig } from 'vitest/config';

import { createProjectNodeModulesFallbackPlugin } from './vitest-utils/project-node-modules-fallback.ts';

import type { UserConfig } from 'vitest/config';

// Loaded with require(), not import: Vite's config bundler chokes on this file's own
// require('fs') when it tries to esbuild-bundle it into the config's ESM graph.
const { requireVueLoaderWithTypeResolutionPatch } = createRequire(import.meta.url)(
    './webpack/webpack-utils/patch-vue-compiler-sfc-type-resolution.js',
);

void requireVueLoaderWithTypeResolutionPatch();

function generateConfig(): Promise<UserConfig> {
    return new Promise((resolve, reject) => {
        const filePath = path.dirname(fileURLToPath(import.meta.url));
        const frontendConfigurationDirectory = path.join(filePath, 'frontend_configuration');

        const exclude = [
            '**/*.d.ts',
            '**/node_modules/**',
            '**/dist/**',
            '**/install/**',
            '**/cypress/**',
            '**/.{idea,git,cache,output,temp}/**',
            '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*',
            '**/build/**',
            '**/staticfiles/**',
        ];

        const rawData = fs.readFileSync(path.join(frontendConfigurationDirectory, 'webpack-metadata.json'), 'utf-8');
        const parsedData = JSON.parse(rawData);

        const alias: { [key: string]: string } = {
            '@/arches': path.join(parsedData['ROOT_DIR'], 'app', 'src', 'arches'),
            'arches': path.join(parsedData['ROOT_DIR'], 'app', 'media', 'js', 'arches.js'),
        };

        for (
            const [archesApplicationName, archesApplicationPath]
            of Object.entries(
                parsedData['ARCHES_APPLICATIONS_PATHS'] as { [key: string]: string }
            )
        ) {
            alias[`@/${archesApplicationName}`] = path.join(archesApplicationPath, 'src', archesApplicationName);
        }

        resolve({
            plugins: [
                vue(),
                createProjectNodeModulesFallbackPlugin(),
            ],
            test: {
                alias: alias,
                coverage: {
                    include: [path.join(parsedData['APP_RELATIVE_PATH'], 'src', path.sep)],
                    exclude: exclude,
                    reporter: [
                        ['clover', { 'file': 'coverage.xml' }],
                        'text',
                    ],
                    reportsDirectory: path.join(filePath, 'coverage', 'frontend'),
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
