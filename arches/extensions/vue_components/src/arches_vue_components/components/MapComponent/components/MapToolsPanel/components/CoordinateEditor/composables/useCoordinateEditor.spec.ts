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
    it("builds and adds a point, then resets for the next entry", () => {
        const context = buildContext();
        const editor = useCoordinateEditor(context, null, "point");

        editor.updateRow(0, "x", -0.1276);
        editor.updateRow(0, "y", 51.5072);
        const shouldClose = editor.submit();

        expect(shouldClose).toBe(false);
        expect(context.addFeatures).toHaveBeenCalledWith([
            {
                type: "Feature",
                properties: {},
                geometry: { type: "Point", coordinates: [-0.1276, 51.5072] },
            },
        ]);
        expect(editor.rows.value).toEqual([{ x: null, y: null }]);
    });

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

    it("keeps the typed rows when the feature limit rejects the shape", () => {
        const context = buildContext();
        vi.mocked(context.addFeatures).mockReturnValue(false);
        const editor = useCoordinateEditor(context, null, "point");

        editor.updateRow(0, "x", 1);
        editor.updateRow(0, "y", 2);

        expect(editor.submit()).toBe(false);
        expect(editor.rows.value).toEqual([{ x: 1, y: 2 }]);
    });

    it("starts in the default kind", () => {
        const editor = useCoordinateEditor(buildContext(), null, "polygon");

        expect(editor.kind.value).toBe("polygon");
        expect(editor.rows.value).toHaveLength(3);
    });

    it("refuses to submit incomplete rows", () => {
        const context = buildContext();
        const editor = useCoordinateEditor(context, null, "point");
        editor.updateRow(0, "x", 1);

        expect(editor.submit()).toBe(false);
        expect(editor.errorMessage.value).not.toBeNull();
        expect(context.addFeatures).not.toHaveBeenCalled();
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

    it("undoes row additions and removals", () => {
        const editor = useCoordinateEditor(buildContext(), null, "point");
        editor.setKind("line");

        editor.addRow(null);
        expect(editor.rows.value).toHaveLength(3);
        editor.removeRow(0);
        expect(editor.rows.value).toHaveLength(2);

        editor.undo();
        expect(editor.rows.value).toHaveLength(3);
        editor.undo();
        expect(editor.rows.value).toHaveLength(2);
        expect(editor.canUndo.value).toBe(false);
    });

    it("records a single undo step per committed row edit", () => {
        const editor = useCoordinateEditor(buildContext(), null, "point");

        editor.beginRowEdit();
        editor.updateRow(0, "x", 1);
        editor.updateRow(0, "x", 12);
        editor.commitRowEdit();

        editor.undo();
        expect(editor.rows.value).toEqual([{ x: null, y: null }]);
        expect(editor.canUndo.value).toBe(false);
    });

    it("applies valid GeoJSON text to the rows", () => {
        const editor = useCoordinateEditor(buildContext(), null, "point");
        const errors = editor.applyGeoJsonText(
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

        expect(editor.applyGeoJsonText("{ broken")).not.toEqual([]);
        expect(
            editor.applyGeoJsonText(
                JSON.stringify({
                    type: "Feature",
                    properties: {},
                    geometry: { type: "MultiPoint", coordinates: [[1, 1]] },
                }),
            ),
        ).toHaveLength(1);
    });
});
