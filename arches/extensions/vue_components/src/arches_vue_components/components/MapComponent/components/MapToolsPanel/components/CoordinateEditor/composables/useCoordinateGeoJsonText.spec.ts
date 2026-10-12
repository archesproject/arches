import { computed, ref, shallowRef } from "vue";
import { describe, expect, it, vi } from "vitest";

import { useCoordinateEditor } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateEditor.ts";
import { useCoordinateGeoJsonText } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateGeoJsonText.ts";

import type { Feature } from "geojson";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

function buildContext(drawnFeatures: Feature[] = []): MapContext {
    return {
        coordinateSystems: ref([
            {
                name: "Geographic",
                srid: "4326",
                proj4: "+proj=longlat +datum=WGS84 +no_defs",
                default: true,
            },
        ]),
        drawnFeatures: shallowRef(drawnFeatures),
        allowedGeometryTypes: computed(() => null),
        addFeatures: vi.fn(() => true),
        updateDrawnFeature: vi.fn(),
    } as unknown as MapContext;
}

describe("useCoordinateGeoJsonText", () => {
    it("applies valid GeoJSON text to the rows", () => {
        const editor = useCoordinateEditor(buildContext(), null, "point");
        const { applyGeoJsonText } = useCoordinateGeoJsonText(editor);
        const errors = applyGeoJsonText(
            JSON.stringify({
                type: "Feature",
                properties: { name: "Typed" },
                geometry: {
                    type: "LineString",
                    coordinates: [
                        [5, 5],
                        [6, 6],
                    ],
                },
            }),
        );

        expect(errors).toEqual([]);
        expect(editor.kind.value).toBe("line");
        expect(editor.rows.value).toEqual([
            { x: 5, y: 5 },
            { x: 6, y: 6 },
        ]);
    });

    it("reports GeoJSON that is not a supported feature", () => {
        const editor = useCoordinateEditor(buildContext(), null, "point");
        const { applyGeoJsonText } = useCoordinateGeoJsonText(editor);

        expect(applyGeoJsonText("{ broken")).not.toEqual([]);
        expect(
            applyGeoJsonText(
                JSON.stringify({
                    type: "Feature",
                    properties: {},
                    geometry: { type: "MultiPoint", coordinates: [[1, 1]] },
                }),
            ),
        ).toHaveLength(1);
    });
});
