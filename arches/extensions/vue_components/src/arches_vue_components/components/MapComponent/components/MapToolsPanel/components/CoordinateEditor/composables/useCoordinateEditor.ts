import { computed, ref } from "vue";

import { useGettext } from "vue3-gettext";

import { WGS84_SRID } from "@/arches_vue_components/components/MapComponent/constants.ts";
import { useCoordinateUndo } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateUndo.ts";
import {
    fromWgs84,
    getCoordinateDecimalPlaces,
    isGeographicCoordinateSystem,
    toWgs84,
} from "@/arches_vue_components/components/MapComponent/utils/coordinate-systems.ts";
import { findGeoJsonErrors } from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";
import {
    KIND_BY_GEOMETRY_TYPE,
    MINIMUM_VERTICES,
    buildGeometry,
    cloneProperties,
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
    GeoJsonError,
} from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/types.ts";
import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

interface CoordinateSnapshot {
    rows: CoordinateRow[];
    properties: Record<string, unknown>;
}

export interface UseCoordinateEditorReturn {
    editingFeature: Feature | null;
    kind: Ref<CoordinateEntryKind>;
    srid: Ref<string>;
    rows: Ref<CoordinateRow[]>;
    errorMessage: Ref<string | null>;
    canUndo: ComputedRef<boolean>;
    decimalPlaces: ComputedRef<number>;
    axisLabels: ComputedRef<{ x: string; y: string }>;
    minimumVertices: ComputedRef<number>;
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
    beginRowEdit: () => void;
    commitRowEdit: () => void;
    undo: () => void;
    getRowWgs84Position: (index: number) => Position | null;
    buildGeoJsonText: () => string;
    applyGeoJsonText: (text: string) => GeoJsonError[];
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
    const { canUndo, pushSnapshot, popSnapshot, clearHistory } =
        useCoordinateUndo<CoordinateSnapshot>();

    const editingFeature: Feature | null =
        drawnFeatures.value.find(
            (feature) => String(feature.id) === editingFeatureId,
        ) ?? null;

    const kind = ref<CoordinateEntryKind>(getInitialKind());
    const srid = ref(
        coordinateSystems.value.find(
            (coordinateSystem) => coordinateSystem.default,
        )?.srid ?? WGS84_SRID,
    );
    const rows = ref<CoordinateRow[]>(getInitialRows());
    const draftProperties = ref<Record<string, unknown>>(
        cloneProperties(editingFeature?.properties),
    );
    const errorMessage = ref<string | null>(null);

    let pendingRowEditSnapshot: CoordinateSnapshot | null = null;

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
            );
        }
        return createEmptyRows(MINIMUM_VERTICES[defaultKind]);
    }

    function roundToDecimalPlaces(value: number, places: number): number {
        return Number(value.toFixed(places));
    }

    function rowsFromWgs84Positions(positions: Position[]): CoordinateRow[] {
        const places = getDecimalPlacesForSrid(srid.value);
        return positions.map((position) => {
            const [xCoordinate, yCoordinate] = fromWgs84(srid.value, position);
            return {
                x: roundToDecimalPlaces(xCoordinate, places),
                y: roundToDecimalPlaces(yCoordinate, places),
            };
        });
    }

    function takeSnapshot(): CoordinateSnapshot {
        return {
            rows: rows.value.map((row) => ({ ...row })),
            properties: cloneProperties(draftProperties.value),
        };
    }

    function recordSnapshot(): void {
        pushSnapshot(takeSnapshot());
    }

    function beginRowEdit(): void {
        pendingRowEditSnapshot = takeSnapshot();
    }

    function commitRowEdit(): void {
        if (
            pendingRowEditSnapshot &&
            JSON.stringify(pendingRowEditSnapshot.rows) !==
                JSON.stringify(rows.value)
        ) {
            pushSnapshot(pendingRowEditSnapshot);
        }
        pendingRowEditSnapshot = null;
    }

    function undo(): void {
        const previousSnapshot = popSnapshot();
        if (!previousSnapshot) {
            return;
        }

        rows.value = previousSnapshot.rows;
        draftProperties.value = previousSnapshot.properties;
    }

    function updateRow(
        index: number,
        axis: keyof CoordinateRow,
        value: number | null,
    ): void {
        rows.value[index][axis] = value;
        errorMessage.value = null;
    }

    function setKind(newKind: CoordinateEntryKind): void {
        kind.value = newKind;
        errorMessage.value = null;
        draftProperties.value = {};
        clearHistory();

        const minimum = MINIMUM_VERTICES[newKind];
        if (newKind === "point") {
            rows.value = rows.value.slice(0, minimum);
        } else if (rows.value.length < minimum) {
            rows.value = [
                ...rows.value,
                ...createEmptyRows(minimum - rows.value.length),
            ];
        }
    }

    function setSrid(newSrid: string): void {
        if (newSrid === srid.value) {
            return;
        }

        recordSnapshot();
        const previousSrid = srid.value;
        const places = getDecimalPlacesForSrid(newSrid);

        rows.value = rows.value.map((row) => {
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
        srid.value = newSrid;
    }

    function addRow(afterIndex: number | null): number {
        recordSnapshot();
        const insertIndex =
            afterIndex === null ? rows.value.length : afterIndex + 1;
        rows.value.splice(insertIndex, 0, { x: null, y: null });
        return insertIndex;
    }

    function removeRow(index: number): void {
        if (rows.value.length <= minimumVertices.value) {
            return;
        }

        recordSnapshot();
        rows.value.splice(index, 1);
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
                properties: draftProperties.value,
                geometry,
            },
            null,
            2,
        );
    }

    function applyGeoJsonText(text: string): GeoJsonError[] {
        const hintErrors = findGeoJsonErrors(text);
        if (hintErrors.length) {
            return hintErrors.map((hint) => ({
                line: hint.line,
                message: hint.message,
            }));
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
                        'Unsupported geometry type "%{type}". Only Point, LineString, and Polygon are supported.',
                        { type: String(parsed.geometry.type) },
                    ),
                },
            ];
        }
        if (editingFeature && parsedKind !== kind.value) {
            return [
                {
                    message: $gettext(
                        "The geometry type cannot change while editing an existing shape.",
                    ),
                },
            ];
        }

        const positions = positionsFromGeometry(parsed.geometry);
        if (positions.length < MINIMUM_VERTICES[parsedKind]) {
            return [
                {
                    message: $gettext(
                        "Not enough valid coordinates for this geometry type.",
                    ),
                },
            ];
        }

        const newRows = rowsFromWgs84Positions(positions);
        const newProperties = cloneProperties(parsed.properties);
        const hasChanged =
            JSON.stringify(newRows) !== JSON.stringify(rows.value) ||
            JSON.stringify(newProperties) !==
                JSON.stringify(draftProperties.value);

        if (hasChanged) {
            recordSnapshot();
            kind.value = parsedKind;
            rows.value = newRows;
            draftProperties.value = newProperties;
        }
        return [];
    }

    function submit(): boolean {
        if (rows.value.length < minimumVertices.value) {
            errorMessage.value = $gettext(
                "This geometry needs at least %{count} vertices.",
                { count: String(minimumVertices.value) },
            );
            return false;
        }
        if (!areAllRowsComplete.value) {
            errorMessage.value = $gettext(
                "Enter a valid number for every coordinate field.",
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
                properties: draftProperties.value,
                geometry,
            });
            return true;
        }

        const wasAdded = addFeatures([
            { type: "Feature", properties: draftProperties.value, geometry },
        ]);
        if (!wasAdded) {
            return false;
        }
        rows.value = createEmptyRows(minimumVertices.value);
        draftProperties.value = {};
        clearHistory();
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
        previewGeometry,
        setKind,
        setSrid,
        updateRow,
        addRow,
        removeRow,
        beginRowEdit,
        commitRowEdit,
        undo,
        getRowWgs84Position,
        buildGeoJsonText,
        applyGeoJsonText,
        submit,
    };
}
