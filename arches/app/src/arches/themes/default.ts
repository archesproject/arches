import { definePreset, palette } from "@primeuix/themes";
import Aura from "@primeuix/themes/aura";

const archesColors = Object.freeze({
    blue: "#579ddb",
    green: "#3acaa1",
    red: "#f75d3f",
});

export const ArchesPreset = definePreset(Aura, {
    primitive: {
        arches: {
            ...archesColors,
            legacy: {
                sidebar: "#2d3c4b",
            },
        },
        blue: palette(archesColors.blue),
        green: palette(archesColors.green),
        red: palette(archesColors.red),
    },
    semantic: {
        // PrimeVue token override
        primary: palette(archesColors.blue),
        // PrimeVue token override
        navigation: {
            list: {
                padding: "0",
            },
            item: {
                padding: "1rem",
            },
            // custom tokens
            header: {
                color: "{arches.legacy.sidebar}",
            },
        },
    },
    components: {
        splitter: {
            handle: {
                background: "{surface.500}",
            },
        },
    },
});

export const DEFAULT_THEME = {
    theme: {
        preset: ArchesPreset,
        options: {
            prefix: "p",
            darkModeSelector: ".arches-dark",
            cssLayer: false,
        },
    },
};
