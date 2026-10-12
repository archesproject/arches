import { computed, ref } from "vue";

import { cloneDeep, isEqual } from "es-toolkit";
import { useGettext } from "vue3-gettext";

import {
    DRAW_MODE_BY_GEOMETRY_TYPE,
    WGS84_SRID,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import {
    getCoordinateDecimalPlaces,
    isGeographicCoordinateSystem,
    toWgs84,
} from "@/arches_vue_components/components/MapComponent/utils/coordinate-systems.ts";
import { useDraftHistory } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useDraftHistory.ts";
import {
    buildGeometry,
    createEmptyRows,
    isRowComplete,
    positionsFromGeometry,
    rowFromWgs84Position,
    toPosition,
} from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/utils/coordinate-rows.ts";

import type { ComputedRef, Ref } from "vue";
import type { Feature, Geometry, Position } from "geojson";

import type { CoordinateRow } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/types.ts";
import type {
    CoordinateSystem,
    DrawMode,
    MapContext,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const MINIMUM_VERTICES: Record<DrawMode, number> = {
    point: 1,
    line: 2,
    polygon: 3,
};

interface CoordinateDraft {
    kind: DrawMode;
    srid: string;
    rows: CoordinateRow[];
    properties: Record<string, unknown>;
}

export interface UseCoordinateEditorReturn {
    editingFeature: Feature | null;
    kind: ComputedRef<DrawMode>;
    srid: ComputedRef<string>;
    rows: ComputedRef<CoordinateRow[]>;
    properties: ComputedRef<Record<string, unknown>>;
    errorMessage: Ref<string | null>;
    canUndo: ComputedRef<boolean>;
    decimalPlaces: ComputedRef<number>;
    axisLabels: ComputedRef<{ x: string; y: string }>;
    minimumVertices: ComputedRef<number>;
    areAllRowsComplete: ComputedRef<boolean>;
    previewGeometry: ComputedRef<Geometry | null>;
    completeGeometry: ComputedRef<Geometry | null>;
    setKind: (newKind: DrawMode) => void;
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
    loadFeature: (feature: Feature) => void;
    submit: () => boolean;
}

export function useCoordinateEditor(
    context: MapContext,
    editingFeatureId: string | null,
    defaultKind: DrawMode,
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

    const history = useDraftHistory(draft);

    const kind = computed(() => draft.value.kind);
    const srid = computed(() => draft.value.srid);
    const rows = computed(() => draft.value.rows);
    const properties = computed(() => draft.value.properties);

    const coordinateSystem = computed(() => findCoordinateSystem(srid.value));

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

    const completeGeometry = computed<Geometry | null>(() => {
        if (!areAllRowsComplete.value) {
            return null;
        }
        return buildGeometry(kind.value, completeWgs84Positions.value);
    });

    function findCoordinateSystem(
        targetSrid: string,
    ): CoordinateSystem | undefined {
        return coordinateSystems.value.find(
            (candidate) => candidate.srid === targetSrid,
        );
    }

    function getInitialKind(): DrawMode {
        if (editingFeature) {
            return DRAW_MODE_BY_GEOMETRY_TYPE[editingFeature.geometry.type];
        }
        return defaultKind;
    }

    function getInitialRows(): CoordinateRow[] {
        if (editingFeature) {
            const initialDecimalPlaces = getCoordinateDecimalPlaces(
                findCoordinateSystem(initialSrid),
            );
            return positionsFromGeometry(editingFeature.geometry).map(
                (position) =>
                    rowFromWgs84Position(
                        position,
                        initialSrid,
                        initialDecimalPlaces,
                    ),
            );
        }
        return createEmptyRows(MINIMUM_VERTICES[defaultKind]);
    }

    function updateRow(
        index: number,
        axis: keyof CoordinateRow,
        value: number | null,
    ): void {
        draft.value.rows[index][axis] = value;
        errorMessage.value = null;
    }

    function setKind(newKind: DrawMode): void {
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
        history.reset();
    }

    function setSrid(newSrid: string): void {
        if (newSrid === srid.value) {
            return;
        }

        const previousSrid = srid.value;
        const newDecimalPlaces = getCoordinateDecimalPlaces(
            findCoordinateSystem(newSrid),
        );

        draft.value.rows = draft.value.rows.map((row) => {
            if (!isRowComplete(row)) {
                return row;
            }
            return rowFromWgs84Position(
                toWgs84(previousSrid, toPosition(row)),
                newSrid,
                newDecimalPlaces,
            );
        });
        draft.value.srid = newSrid;
        history.commit();
    }

    function addRow(afterIndex: number | null): number {
        let insertIndex = draft.value.rows.length;
        if (afterIndex !== null) {
            insertIndex = afterIndex + 1;
        }
        draft.value.rows.splice(insertIndex, 0, { x: null, y: null });
        history.commit();
        return insertIndex;
    }

    function removeRow(index: number): void {
        if (draft.value.rows.length <= minimumVertices.value) {
            return;
        }

        draft.value.rows.splice(index, 1);
        history.commit();
    }

    function getRowWgs84Position(index: number): Position | null {
        const row = rows.value[index];
        if (!row || !isRowComplete(row)) {
            return null;
        }
        return toWgs84(srid.value, toPosition(row));
    }

    function loadFeature(feature: Feature): void {
        const loadedDraft: CoordinateDraft = {
            kind: DRAW_MODE_BY_GEOMETRY_TYPE[feature.geometry.type],
            srid: srid.value,
            rows: positionsFromGeometry(feature.geometry).map((position) =>
                rowFromWgs84Position(position, srid.value, decimalPlaces.value),
            ),
            properties: cloneDeep(feature.properties ?? {}),
        };
        if (isEqual(loadedDraft, draft.value)) {
            return;
        }

        draft.value = loadedDraft;
        history.commit();
    }

    function submit(): boolean {
        const geometry = completeGeometry.value;
        if (!geometry) {
            errorMessage.value = $gettext(
                "Enter a valid number for every X and Y field.",
            );
            return false;
        }
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
        history.reset();
        return false;
    }

    return {
        editingFeature,
        kind,
        srid,
        rows,
        properties,
        errorMessage,
        canUndo: history.canUndo,
        decimalPlaces,
        axisLabels,
        minimumVertices,
        areAllRowsComplete,
        previewGeometry,
        completeGeometry,
        setKind,
        setSrid,
        updateRow,
        addRow,
        removeRow,
        commitRowEdit: history.commitIfChanged,
        undo: history.undo,
        getRowWgs84Position,
        loadFeature,
        submit,
    };
}
