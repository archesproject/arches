import proj4 from "proj4";

import { WGS84_SRID } from "@/arches_vue_components/components/MapComponent/constants.ts";

import type { Position } from "geojson";
import type { CoordinateSystem } from "@/arches_vue_components/components/MapComponent/types.ts";

const GEOGRAPHIC_PROJECTION_PATTERN = /\+proj=longlat/;
const GEOGRAPHIC_DECIMAL_PLACES = 6;
const PROJECTED_DECIMAL_PLACES = 2;

function toProjectionCode(srid: string): string {
    return `EPSG:${srid}`;
}

export function registerCoordinateSystems(
    coordinateSystems: CoordinateSystem[],
): void {
    for (const coordinateSystem of coordinateSystems) {
        proj4.defs(
            toProjectionCode(coordinateSystem.srid),
            coordinateSystem.proj4,
        );
    }
}

export function isGeographicCoordinateSystem(
    coordinateSystem: CoordinateSystem,
): boolean {
    return GEOGRAPHIC_PROJECTION_PATTERN.test(coordinateSystem.proj4);
}

export function getCoordinateDecimalPlaces(
    coordinateSystem: CoordinateSystem | undefined,
): number {
    if (!coordinateSystem || isGeographicCoordinateSystem(coordinateSystem)) {
        return GEOGRAPHIC_DECIMAL_PLACES;
    }
    return PROJECTED_DECIMAL_PLACES;
}

export function toWgs84(srid: string, position: Position): Position {
    if (srid === WGS84_SRID) {
        return position;
    }
    return proj4(
        toProjectionCode(srid),
        toProjectionCode(WGS84_SRID),
        position,
    );
}

export function fromWgs84(srid: string, position: Position): Position {
    if (srid === WGS84_SRID) {
        return position;
    }
    return proj4(
        toProjectionCode(WGS84_SRID),
        toProjectionCode(srid),
        position,
    );
}
