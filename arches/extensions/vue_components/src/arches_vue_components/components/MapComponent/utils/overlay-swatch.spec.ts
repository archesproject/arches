import { describe, expect, it } from "vitest";

import { deriveOverlaySwatch } from "@/arches_vue_components/components/MapComponent/utils/overlay-swatch.ts";

import type { MapLayer } from "@/arches_vue_components/components/MapComponent/types.ts";

function buildOverlay(overrides: Partial<MapLayer>): MapLayer {
    return {
        id: 1,
        maplayerid: "overlay-1",
        name: "Overlay",
        addtomap: true,
        layerdefinitions: [],
        ...overrides,
    };
}

describe("deriveOverlaySwatch", () => {
    it("skips halo, hover and click layers when choosing a color", () => {
        const overlay = buildOverlay({
            layerdefinitions: [
                {
                    id: "resources-point-halo-1",
                    type: "circle",
                    paint: { "circle-color": "#ffffff" },
                },
                {
                    id: "resources-fill-1-hover",
                    type: "fill",
                    paint: { "fill-color": "#000000" },
                },
                {
                    id: "resources-fill-1",
                    type: "fill",
                    paint: { "fill-color": "#ff0000" },
                },
            ],
        });
        expect(deriveOverlaySwatch(overlay)).toEqual({
            kind: "fill",
            color: "#ff0000",
        });
    });

    it("maps circle layers to point swatches", () => {
        const overlay = buildOverlay({
            layerdefinitions: [
                {
                    id: "points",
                    type: "circle",
                    paint: { "circle-color": "#00ff00" },
                },
            ],
        });
        expect(deriveOverlaySwatch(overlay)).toEqual({
            kind: "point",
            color: "#00ff00",
        });
    });

    it("builds a gradient from heatmap color stops", () => {
        const overlay = buildOverlay({
            layerdefinitions: [
                {
                    id: "heat",
                    type: "heatmap",
                    paint: {
                        "heatmap-color": [
                            "interpolate",
                            ["linear"],
                            ["heatmap-density"],
                            0,
                            "rgba(0,0,0,0)",
                            1,
                            "#ff0000",
                        ],
                    },
                },
            ],
        });
        expect(deriveOverlaySwatch(overlay)).toEqual({
            kind: "gradient",
            colors: ["rgba(0,0,0,0)", "#ff0000"],
        });
    });

    it("falls back to the overlay icon when no literal color exists", () => {
        const overlay = buildOverlay({
            icon: "fa fa-map",
            layerdefinitions: [
                {
                    id: "fill",
                    type: "fill",
                    paint: { "fill-color": ["get", "color"] },
                },
            ],
        });
        expect(deriveOverlaySwatch(overlay)).toEqual({
            kind: "icon",
            iconClass: "fa fa-map",
        });
    });

    it("returns null when nothing describes the overlay", () => {
        expect(deriveOverlaySwatch(buildOverlay({}))).toBeNull();
    });
});
