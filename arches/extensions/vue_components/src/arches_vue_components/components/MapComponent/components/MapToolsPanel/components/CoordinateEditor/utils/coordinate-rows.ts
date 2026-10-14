import { fromWgs84 } from "@/arches_vue_components/components/MapComponent/utils/coordinate-systems.ts";

import type { Geometry, Position } from "geojson";

import type {
    CoordinateRow,
    DrawMode,
} from "@/arches_vue_components/components/MapComponent/types.ts";

export function createEmptyRows(count: number): CoordinateRow[] {
    return Array.from({ length: count }, () => ({ x: null, y: null }));
}

export function isRowComplete(
    row: CoordinateRow,
): row is Record<keyof CoordinateRow, number> {
    return Number.isFinite(row.x) && Number.isFinite(row.y);
}

export function toPosition(row: Record<keyof CoordinateRow, number>): Position {
    return [row.x, row.y];
}

export function rowFromWgs84Position(
    position: Position,
    srid: string,
    decimalPlaces: number,
): CoordinateRow {
    const [xCoordinate, yCoordinate] = fromWgs84(srid, position);
    return {
        x: Number(xCoordinate.toFixed(decimalPlaces)),
        y: Number(yCoordinate.toFixed(decimalPlaces)),
    };
}

export function positionsFromGeometry(geometry: Geometry): Position[] {
    if (geometry.type === "Point") {
        return [geometry.coordinates];
    }
    if (geometry.type === "LineString") {
        return geometry.coordinates;
    }
    if (geometry.type === "Polygon") {
        return geometry.coordinates[0].slice(0, -1);
    }
    return [];
}

export function buildGeometry(kind: DrawMode, positions: Position[]): Geometry {
    if (kind === "point") {
        return { type: "Point", coordinates: positions[0] };
    }
    if (kind === "line") {
        return { type: "LineString", coordinates: positions };
    }
    return { type: "Polygon", coordinates: [[...positions, positions[0]]] };
}
