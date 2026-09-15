import type { PrimeVueConfiguration as OpenVueConfiguration } from "openvue/config";

export type ArchesThemeConfiguration = OpenVueConfiguration & {
    theme: {
        options: {
            darkModeSelector: string;
            [key: string]: unknown;
        };
        [key: string]: unknown;
    };
};
