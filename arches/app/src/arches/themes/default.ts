import { definePreset, palette } from "@primevue/themes";
import Aura from "@primevue/themes/aura";

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
        green: palette(archesColors.green),
        red: palette(archesColors.red),
    },
    semantic: {
        primary: palette(archesColors.blue),
        navigation: {
            list: {
                padding: "0",
            },
            item: {
                padding: "1rem",
            },
            color: "{arches.legacy.sidebar}",
        },
        iconSize: "small",
        // Additional tokens
        content: {
            gap: "1rem",
        },
    },
    components: {
        button: {
            root: {
                label: {
                    fontWeight: 600,
                },
            },
        },
        menubar: {
            border: {
                radius: 0,
            },
        },
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
            darkModeSelector: "system",
            cssLayer: false,
        },
    },
};
