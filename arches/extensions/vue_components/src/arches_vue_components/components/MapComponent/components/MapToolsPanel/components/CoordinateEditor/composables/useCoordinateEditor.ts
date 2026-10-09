import { computed, ref, shallowRef } from "vue";

import { cloneDeep, isEqual } from "es-toolkit";
import { useGettext } from "vue3-gettext";

import { WGS84_SRID } from "@/arches_vue_components/components/MapComponent/constants.ts";
import {
    fromWgs84,
    getCoordinateDecimalPlaces,
    isGeographicCoordinateSystem,
    toWgs84,
} from "@/arches_vue_components/components/MapComponent/utils/coordinate-systems.ts";
import { findGeoJsonIssues } from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";
import {
    KIND_BY_GEOMETRY_TYPE,
    MINIMUM_VERTICES,
    buildGeometry,
    createEmptyRows,
    isRowComplete,
    positionsFromGeometry,
    toPosition,
} from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/utils/coordinate-rows.ts";

import type { ComputedRef, Ref } from "vue";
import type { Feature, Geometry, Position } from "geojson";

import type {
    CoordinateEntryKind,
    CoordinateRow,
} from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/types.ts";
import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";
import type { GeoJsonIssue } from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";

const UNDO_HISTORY_LIMIT = 50;

interface CoordinateDraft {
    kind: CoordinateEntryKind;
    srid: string;
    rows: CoordinateRow[];
    properties: Record<string, unknown>;
}

export interface UseCoordinateEditorReturn {
    editingFeature: Feature | null;
    kind: ComputedRef<CoordinateEntryKind>;
    srid: ComputedRef<string>;
    rows: ComputedRef<CoordinateRow[]>;
    errorMessage: Ref<string | null>;
    canUndo: ComputedRef<boolean>;
    decimalPlaces: ComputedRef<number>;
    axisLabels: ComputedRef<{ x: string; y: string }>;
    minimumVertices: ComputedRef<number>;
    areAllRowsComplete: ComputedRef<boolean>;
    previewGeometry: ComputedRef<Geometry | null>;
    setKind: (newKind: CoordinateEntryKind) => void;
    setSrid: (newSrid: string) => void;
    updateRow: (
        index: number,
        axis: keyof CoordinateRow,
        value: number | null,
    ) => void;
    addRow: (afterIndex: number | null) => number;
    removeRow: (index: number) => void;
    commitRowEdit: () => void;
    undo: () => void;
    getRowWgs84Position: (index: number) => Position | null;
    buildGeoJsonText: () => string;
    applyGeoJsonText: (text: string) => GeoJsonIssue[];
    submit: () => boolean;
}

export function useCoordinateEditor(
    context: MapContext,
    editingFeatureId: string | null,
    defaultKind: CoordinateEntryKind,
): UseCoordinateEditorReturn {
    const { $gettext } = useGettext();

    const {
        coordinateSystems,
        drawnFeatures,
        addFeatures,
        updateDrawnFeature,
    } = context;

    const editingFeature: Feature | null =
        drawnFeatures.value.find(
            (feature) => String(feature.id) === editingFeatureId,
        ) ?? null;
    const initialSrid =
        coordinateSystems.value.find(
            (coordinateSystem) => coordinateSystem.default,
        )?.srid ?? WGS84_SRID;

    const draft = ref<CoordinateDraft>({
        kind: getInitialKind(),
        srid: initialSrid,
        rows: getInitialRows(),
        properties: cloneDeep(editingFeature?.properties ?? {}),
    });
    const errorMessage = ref<string | null>(null);

    const undoStack = shallowRef<CoordinateDraft[]>([]);

    let committedDraft = cloneDeep(draft.value);

    const canUndo = computed(() => undoStack.value.length > 0);
    const kind = computed(() => draft.value.kind);
    const srid = computed(() => draft.value.srid);
    const rows = computed(() => draft.value.rows);

    const coordinateSystem = computed(() =>
        coordinateSystems.value.find(
            (candidate) => candidate.srid === srid.value,
        ),
    );

    const decimalPlaces = computed(() =>
        getCoordinateDecimalPlaces(coordinateSystem.value),
    );

    const axisLabels = computed(() => {
        if (
            coordinateSystem.value &&
            !isGeographicCoordinateSystem(coordinateSystem.value)
        ) {
            return { x: $gettext("Easting"), y: $gettext("Northing") };
        }
        return { x: $gettext("Longitude"), y: $gettext("Latitude") };
    });

    const minimumVertices = computed(() => MINIMUM_VERTICES[kind.value]);

    const completeWgs84Positions = computed(() =>
        rows.value
            .filter(isRowComplete)
            .map((row) => toWgs84(srid.value, toPosition(row))),
    );

    const areAllRowsComplete = computed(
        () =>
            rows.value.length >= minimumVertices.value &&
            rows.value.every(isRowComplete),
    );

    const previewGeometry = computed<Geometry | null>(() => {
        const positions = completeWgs84Positions.value;
        if (positions.length >= minimumVertices.value) {
            return buildGeometry(kind.value, positions);
        }
        if (positions.length) {
            return { type: "MultiPoint", coordinates: positions };
        }
        return null;
    });

    function getDecimalPlacesForSrid(targetSrid: string): number {
        return getCoordinateDecimalPlaces(
            coordinateSystems.value.find(
                (candidate) => candidate.srid === targetSrid,
            ),
        );
    }

    function getInitialKind(): CoordinateEntryKind {
        if (editingFeature) {
            return KIND_BY_GEOMETRY_TYPE[editingFeature.geometry.type];
        }
        return defaultKind;
    }

    function getInitialRows(): CoordinateRow[] {
        if (editingFeature) {
            return rowsFromWgs84Positions(
                positionsFromGeometry(editingFeature.geometry),
                initialSrid,
            );
        }
        return createEmptyRows(MINIMUM_VERTICES[defaultKind]);
    }

    function getKindLabel(entryKind: CoordinateEntryKind): string {
        if (entryKind === "point") {
            return $gettext("Point");
        }
        if (entryKind === "line") {
            return $gettext("Line");
        }
        return $gettext("Polygon");
    }

    function getMinimumVerticesMessage(
        entryKind: CoordinateEntryKind,
        count: number,
    ): string {
        const parameters = { count: String(count) };
        if (entryKind === "point") {
            return $gettext(
                "A point needs at least %{count} vertices.",
                parameters,
            );
        }
        if (entryKind === "line") {
            return $gettext(
                "A line needs at least %{count} vertices.",
                parameters,
            );
        }
        return $gettext(
            "A polygon needs at least %{count} vertices.",
            parameters,
        );
    }

    function getNotEnoughCoordinatesMessage(
        entryKind: CoordinateEntryKind,
    ): string {
        if (entryKind === "point") {
            return $gettext("Not enough valid coordinates for a point.");
        }
        if (entryKind === "line") {
            return $gettext("Not enough valid coordinates for a line.");
        }
        return $gettext("Not enough valid coordinates for a polygon.");
    }

    function roundToDecimalPlaces(value: number, places: number): number {
        return Number(value.toFixed(places));
    }

    function rowsFromWgs84Positions(
        positions: Position[],
        targetSrid: string,
    ): CoordinateRow[] {
        const places = getDecimalPlacesForSrid(targetSrid);
        return positions.map((position) => {
            const [xCoordinate, yCoordinate] = fromWgs84(targetSrid, position);
            return {
                x: roundToDecimalPlaces(xCoordinate, places),
                y: roundToDecimalPlaces(yCoordinate, places),
            };
        });
    }

    function commit(): void {
        undoStack.value = [...undoStack.value, committedDraft].slice(
            -UNDO_HISTORY_LIMIT,
        );
        committedDraft = cloneDeep(draft.value);
    }

    function undo(): void {
        const previousDraft = undoStack.value.at(-1);
        if (!previousDraft) {
            return;
        }

        undoStack.value = undoStack.value.slice(0, -1);
        committedDraft = previousDraft;
        draft.value = cloneDeep(previousDraft);
    }

    function resetHistory(): void {
        undoStack.value = [];
        committedDraft = cloneDeep(draft.value);
    }

    function commitRowEdit(): void {
        if (!isEqual(draft.value, committedDraft)) {
            commit();
        }
    }

    function updateRow(
        index: number,
        axis: keyof CoordinateRow,
        value: number | null,
    ): void {
        draft.value.rows[index][axis] = value;
        errorMessage.value = null;
    }

    function setKind(newKind: CoordinateEntryKind): void {
        const minimum = MINIMUM_VERTICES[newKind];
        draft.value.kind = newKind;
        draft.value.properties = {};
        errorMessage.value = null;

        if (newKind === "point") {
            draft.value.rows = draft.value.rows.slice(0, minimum);
        } else if (draft.value.rows.length < minimum) {
            draft.value.rows = [
                ...draft.value.rows,
                ...createEmptyRows(minimum - draft.value.rows.length),
            ];
        }
        resetHistory();
    }

    function setSrid(newSrid: string): void {
        if (newSrid === srid.value) {
            return;
        }

        const previousSrid = srid.value;
        const places = getDecimalPlacesForSrid(newSrid);

        draft.value.rows = draft.value.rows.map((row) => {
            if (!isRowComplete(row)) {
                return row;
            }
            const [xCoordinate, yCoordinate] = fromWgs84(
                newSrid,
                toWgs84(previousSrid, toPosition(row)),
            );
            return {
                x: roundToDecimalPlaces(xCoordinate, places),
                y: roundToDecimalPlaces(yCoordinate, places),
            };
        });
        draft.value.srid = newSrid;
        commit();
    }

    function addRow(afterIndex: number | null): number {
        let insertIndex = draft.value.rows.length;
        if (afterIndex !== null) {
            insertIndex = afterIndex + 1;
        }
        draft.value.rows.splice(insertIndex, 0, { x: null, y: null });
        commit();
        return insertIndex;
    }

    function removeRow(index: number): void {
        if (draft.value.rows.length <= minimumVertices.value) {
            return;
        }

        draft.value.rows.splice(index, 1);
        commit();
    }

    function getRowWgs84Position(index: number): Position | null {
        const row = rows.value[index];
        if (!row || !isRowComplete(row)) {
            return null;
        }
        return toWgs84(srid.value, toPosition(row));
    }

    function buildGeoJsonText(): string {
        let geometry: Geometry | null = null;
        if (areAllRowsComplete.value) {
            geometry = buildGeometry(kind.value, completeWgs84Positions.value);
        }
        return JSON.stringify(
            {
                type: "Feature",
                properties: draft.value.properties,
                geometry,
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

        const parsed = JSON.parse(text);
        if (parsed?.type !== "Feature" || !parsed.geometry) {
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

        const positions = positionsFromGeometry(parsed.geometry);
        if (positions.length < MINIMUM_VERTICES[parsedKind]) {
            return [
                {
                    message: getNotEnoughCoordinatesMessage(parsedKind),
                },
            ];
        }

        const newRows = rowsFromWgs84Positions(positions, srid.value);
        const newProperties = cloneDeep(parsed.properties ?? {});
        const hasChanged =
            !isEqual(newRows, draft.value.rows) ||
            !isEqual(newProperties, draft.value.properties);

        if (hasChanged) {
            draft.value.kind = parsedKind;
            draft.value.rows = newRows;
            draft.value.properties = newProperties;
            commit();
        }
        return [];
    }

    function submit(): boolean {
        if (rows.value.length < minimumVertices.value) {
            errorMessage.value = getMinimumVerticesMessage(
                kind.value,
                minimumVertices.value,
            );
            return false;
        }
        if (!areAllRowsComplete.value) {
            errorMessage.value = $gettext(
                "Enter a valid number for every X and Y field.",
            );
            return false;
        }

        const geometry = buildGeometry(
            kind.value,
            completeWgs84Positions.value,
        );
        errorMessage.value = null;

        if (editingFeature) {
            updateDrawnFeature({
                type: "Feature",
                id: editingFeature.id,
                properties: cloneDeep(draft.value.properties),
                geometry,
            });
            return true;
        }

        const wasAdded = addFeatures([
            {
                type: "Feature",
                properties: cloneDeep(draft.value.properties),
                geometry,
            },
        ]);
        if (!wasAdded) {
            return false;
        }
        draft.value.rows = createEmptyRows(minimumVertices.value);
        draft.value.properties = {};
        resetHistory();
        return false;
    }

    return {
        editingFeature,
        kind,
        srid,
        rows,
        errorMessage,
        canUndo,
        decimalPlaces,
        axisLabels,
        minimumVertices,
        areAllRowsComplete,
        previewGeometry,
        setKind,
        setSrid,
        updateRow,
        addRow,
        removeRow,
        commitRowEdit,
        undo,
        getRowWgs84Position,
        buildGeoJsonText,
        applyGeoJsonText,
        submit,
    };
}
