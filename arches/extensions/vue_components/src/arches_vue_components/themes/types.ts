import type { PrimeVueConfiguration } from "primevue/config";

export type ArchesThemeConfiguration = PrimeVueConfiguration & {
    theme: {
        options: {
            darkModeSelector: string;
            [key: string]: unknown;
        };
        [key: string]: unknown;
    };
};
