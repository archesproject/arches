import { describe, expect, it } from "vitest";

import {
    buildScaledOpacityPaint,
    isOverlayOpacityAdjustable,
} from "@/arches_vue_components/components/MapComponent/utils/overlay-opacity.ts";

describe("overlay opacity", () => {
    it("is adjustable when every opacity is a literal or unset", () => {
        expect(
            isOverlayOpacityAdjustable([
                { id: "fill", type: "fill", paint: { "fill-opacity": 0.5 } },
                { id: "line", type: "line" },
            ]),
        ).toBe(true);
    });

    it("is not adjustable when any opacity is an expression", () => {
        expect(
            isOverlayOpacityAdjustable([
                {
                    id: "points",
                    type: "circle",
                    paint: {
                        "circle-opacity": [
                            "interpolate",
                            ["linear"],
                            ["zoom"],
                            5,
                            0,
                            10,
                            1,
                        ],
                    },
                },
            ]),
        ).toBe(false);
    });

    it("scales literal opacities and defaults unset ones to fully opaque", () => {
        expect(
            buildScaledOpacityPaint(
                {
                    id: "points",
                    type: "circle",
                    paint: { "circle-opacity": 0.8 },
                },
                50,
            ),
        ).toEqual([
            ["circle-opacity", 0.4],
            ["circle-stroke-opacity", 0.5],
        ]);
    });

    it("returns nothing for layer types without opacity properties", () => {
        expect(
            buildScaledOpacityPaint({ id: "shade", type: "hillshade" }, 50),
        ).toEqual([]);
    });
});
