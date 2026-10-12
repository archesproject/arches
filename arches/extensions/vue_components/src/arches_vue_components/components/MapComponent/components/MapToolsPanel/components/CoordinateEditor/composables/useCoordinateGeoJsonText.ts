import { useGettext } from "vue3-gettext";

import { findGeoJsonIssues } from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";
import { KIND_BY_GEOMETRY_TYPE } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/utils/coordinate-rows.ts";

import type { GeoJSON } from "geojson";

import type { UseCoordinateEditorReturn } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateEditor.ts";
import type { CoordinateEntryKind } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/types.ts";
import type { GeoJsonIssue } from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";

export interface UseCoordinateGeoJsonTextReturn {
    buildGeoJsonText: () => string;
    applyGeoJsonText: (text: string) => GeoJsonIssue[];
}

export function useCoordinateGeoJsonText(
    coordinateEditor: UseCoordinateEditorReturn,
): UseCoordinateGeoJsonTextReturn {
    const { $gettext } = useGettext();

    const { editingFeature, kind, properties, completeGeometry, loadFeature } =
        coordinateEditor;

    function getKindLabel(entryKind: CoordinateEntryKind): string {
        if (entryKind === "point") {
            return $gettext("Point");
        }
        if (entryKind === "line") {
            return $gettext("Line");
        }
        return $gettext("Polygon");
    }

    function buildGeoJsonText(): string {
        return JSON.stringify(
            {
                type: "Feature",
                properties: properties.value,
                geometry: completeGeometry.value,
            },
            null,
            2,
        );
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

        const parsedKind = KIND_BY_GEOMETRY_TYPE[parsed.geometry.type];
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

    return { buildGeoJsonText, applyGeoJsonText };
}
