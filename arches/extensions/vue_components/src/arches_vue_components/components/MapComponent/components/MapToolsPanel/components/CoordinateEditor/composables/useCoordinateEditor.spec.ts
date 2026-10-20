import { computed, ref, shallowRef } from "vue";
import { describe, expect, it, vi } from "vitest";

import { useCoordinateEditor } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateEditor.ts";

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

describe("useCoordinateEditor", () => {
    it("closes the polygon ring when submitting", () => {
        const context = buildContext();
        const editor = useCoordinateEditor(context, null, "point");
        editor.setKind("polygon");

        [
            [0, 0],
            [1, 0],
            [1, 1],
        ].forEach(([xCoordinate, yCoordinate], index) => {
            editor.updateRow(index, "x", xCoordinate);
            editor.updateRow(index, "y", yCoordinate);
        });
        editor.submit();

        expect(context.addFeatures).toHaveBeenCalledWith([
            expect.objectContaining({
                geometry: {
                    type: "Polygon",
                    coordinates: [
                        [
                            [0, 0],
                            [1, 0],
                            [1, 1],
                            [0, 0],
                        ],
                    ],
                },
            }),
        ]);
    });

    it("loads an existing line and updates it in place", () => {
        const existingLine: Feature = {
            type: "Feature",
            id: "line-1",
            properties: { buffer_distance: 0 },
            geometry: {
                type: "LineString",
                coordinates: [
                    [0, 0],
                    [2, 2],
                ],
            },
        };
        const context = buildContext([existingLine]);
        const editor = useCoordinateEditor(context, "line-1", "point");

        expect(editor.kind.value).toBe("line");
        expect(editor.rows.value).toEqual([
            { x: 0, y: 0 },
            { x: 2, y: 2 },
        ]);

        editor.updateRow(1, "x", 3);
        expect(editor.submit()).toBe(true);
        expect(context.updateDrawnFeature).toHaveBeenCalledWith({
            type: "Feature",
            id: "line-1",
            properties: { buffer_distance: 0 },
            geometry: {
                type: "LineString",
                coordinates: [
                    [0, 0],
                    [3, 2],
                ],
            },
        });
    });

    it("records a single undo step per committed row edit", () => {
        const editor = useCoordinateEditor(buildContext(), null, "point");

        editor.updateRow(0, "x", 1);
        editor.updateRow(0, "x", 12);
        editor.commitRowEdit();

        editor.undo();
        expect(editor.rows.value).toEqual([{ x: null, y: null }]);
        expect(editor.canUndo.value).toBe(false);
    });
});
