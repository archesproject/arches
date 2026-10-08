import type { Geometry, Position } from "geojson";

import type {
    CompleteCoordinateRow,
    CoordinateEntryKind,
    CoordinateRow,
} from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/types.ts";

export const MINIMUM_VERTICES: Record<CoordinateEntryKind, number> = {
    point: 1,
    line: 2,
    polygon: 3,
};

export const KIND_BY_GEOMETRY_TYPE: Record<string, CoordinateEntryKind> = {
    Point: "point",
    LineString: "line",
    Polygon: "polygon",
};

export function createEmptyRows(count: number): CoordinateRow[] {
    return Array.from({ length: count }, () => ({ x: null, y: null }));
}

export function isRowComplete(
    row: CoordinateRow,
): row is CompleteCoordinateRow {
    return (
        row.x !== null &&
        row.y !== null &&
        Number.isFinite(row.x) &&
        Number.isFinite(row.y)
    );
}

export function toPosition(row: CompleteCoordinateRow): Position {
    return [row.x, row.y];
}

export function positionsFromGeometry(geometry: Geometry): Position[] {
    if (geometry.type === "Point") {
        return [geometry.coordinates];
    }
    if (geometry.type === "LineString") {
        return geometry.coordinates;
    }
    if (geometry.type === "Polygon") {
        return (geometry.coordinates[0] ?? []).slice(0, -1);
    }
    return [];
}

export function buildGeometry(
    kind: CoordinateEntryKind,
    positions: Position[],
): Geometry {
    if (kind === "point") {
        return { type: "Point", coordinates: positions[0] };
    }
    if (kind === "line") {
        return { type: "LineString", coordinates: positions };
    }
    return { type: "Polygon", coordinates: [[...positions, positions[0]]] };
}

export function cloneProperties(
    properties: Record<string, unknown> | null | undefined,
): Record<string, unknown> {
    return JSON.parse(JSON.stringify(properties ?? {}));
}
