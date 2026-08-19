import { definePreset, palette } from "@primeuix/themes";

// eslint-disable-next-line
// @ts-ignore: This is a workaround for PrimeVue theme import issues after v1.20
import Aura from "@primeuix/themes/aura";

const archesColors = Object.freeze({
    blue: "#579ddb",
    green: "#3acaa1",
    red: "#f75d3f",
});

/**
 * @deprecated Use ArchesPreset from arches-vue-components instead.
 * @see import { ArchesPreset } from '@/arches_vue_components/themes'
 */
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

/**
 * @deprecated Use DEFAULT_THEME from arches-vue-components instead.
 * @see import { DEFAULT_THEME } from '@/arches_vue_components/themes'
 */
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
