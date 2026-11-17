import { onScopeDispose, ref } from "vue";

import { debounce } from "es-toolkit";
import { useGettext } from "vue3-gettext";

import { DRAW_MODE_BY_GEOMETRY_TYPE } from "@/arches_vue_components/components/MapComponent/constants.ts";
import { findGeoJsonIssues } from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";

import type { Ref } from "vue";
import type { GeoJSON } from "geojson";

import type { UseCoordinateEditorReturn } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateEditor.ts";
import type { DrawMode } from "@/arches_vue_components/components/MapComponent/types.ts";
import type { GeoJsonIssue } from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";

const APPLY_DEBOUNCE_MILLISECONDS = 200;

export interface UseCoordinateGeoJsonTextReturn {
    geoJsonText: Ref<string>;
    geoJsonErrors: Ref<GeoJsonIssue[]>;
    resetGeoJsonText: () => void;
    updateGeoJsonText: (text: string) => void;
    flushGeoJsonText: () => void;
}

export function useCoordinateGeoJsonText(
    coordinateEditor: UseCoordinateEditorReturn,
): UseCoordinateGeoJsonTextReturn {
    const { $gettext } = useGettext();

    const { editingFeature, kind, properties, completeGeometry, loadFeature } =
        coordinateEditor;

    const geoJsonText = ref("");
    const geoJsonErrors = ref<GeoJsonIssue[]>([]);

    const applyGeoJsonTextDebounced = debounce(() => {
        geoJsonErrors.value = applyGeoJsonText(geoJsonText.value);
    }, APPLY_DEBOUNCE_MILLISECONDS);

    onScopeDispose(() => {
        applyGeoJsonTextDebounced.cancel();
    });

    function resetGeoJsonText(): void {
        applyGeoJsonTextDebounced.cancel();
        geoJsonText.value = JSON.stringify(
            {
                type: "Feature",
                properties: properties.value,
                geometry: completeGeometry.value,
            },
            null,
            2,
        );
        geoJsonErrors.value = [];
    }

    function updateGeoJsonText(text: string): void {
        geoJsonText.value = text;
        applyGeoJsonTextDebounced();
    }

    function flushGeoJsonText(): void {
        applyGeoJsonTextDebounced.flush();
    }

    function getKindLabel(entryKind: DrawMode): string {
        if (entryKind === "point") {
            return $gettext("Point");
        }
        if (entryKind === "line") {
            return $gettext("Line");
        }
        return $gettext("Polygon");
    }

    function applyGeoJsonText(text: string): GeoJsonIssue[] {
        const issues = findGeoJsonIssues(text);
        if (issues.length) {
            return issues;
        }

        const parsed: GeoJSON = JSON.parse(text);
        if (parsed.type !== "Feature" || !parsed.geometry) {
            return [
                {
                    message: $gettext(
                        "Must be a GeoJSON Feature with a geometry.",
                    ),
                },
            ];
        }

        const parsedKind = DRAW_MODE_BY_GEOMETRY_TYPE[parsed.geometry.type];
        if (!parsedKind) {
            return [
                {
                    message: $gettext(
                        'Unsupported geometry type "%{type}" — only Point, LineString, and Polygon are supported.',
                        { type: String(parsed.geometry.type) },
                    ),
                },
            ];
        }
        if (editingFeature && parsedKind !== kind.value) {
            return [
                {
                    message: $gettext(
                        "Geometry type must stay %{kind} while editing this shape.",
                        { kind: getKindLabel(kind.value) },
                    ),
                },
            ];
        }

        loadFeature(parsed);
        return [];
    }

    return {
        geoJsonText,
        geoJsonErrors,
        resetGeoJsonText,
        updateGeoJsonText,
        flushGeoJsonText,
    };
}
