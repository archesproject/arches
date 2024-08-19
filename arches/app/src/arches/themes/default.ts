import { definePreset } from "@primevue/themes";
import Aura from "@primevue/themes/aura";

export const ArchesPreset = definePreset(Aura, {
    primitive: {
        arches: {
            blue: {
                400: "#54abd9", // legacy paginator button color
                500: "#579ddb", // legacy light button color
                600: "#2986b8", // legacy sidebar highlight
                950: "#2d3c4b", // legacy sidebar
            },
        },
    },
    semantic: {
        primary: {
            50: "{sky.50}",
            100: "{sky.100}",
            200: "{sky.200}",
            300: "{sky.300}",
            400: "{sky.400}",
            500: "{sky.500}",
            600: "{sky.600}",
            700: "{sky.700}",
            800: "{sky.800}",
            900: "{sky.900}",
            950: "{sky.950}",
        },
        navigation: "{arches.blue.950}",
    },
    components: {
        button: {
            root: {
                label: {
                    fontWeight: 600,
                },
            },
        },
        datatable: {
            column: {
                title: {
                    fontWeight: 600,
                },
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
            cssLayer: true,
        },
    },
};
