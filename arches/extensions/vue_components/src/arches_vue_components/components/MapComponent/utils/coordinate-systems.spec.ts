import { describe, expect, it } from "vitest";

import {
    fromWgs84,
    getCoordinateDecimalPlaces,
    isGeographicCoordinateSystem,
    registerCoordinateSystems,
    toWgs84,
} from "@/arches_vue_components/components/MapComponent/utils/coordinate-systems.ts";

const GEOGRAPHIC = {
    name: "Geographic",
    srid: "4326",
    proj4: "+proj=longlat +datum=WGS84 +no_defs",
    default: true,
};
const BRITISH_NATIONAL_GRID = {
    name: "British National Grid",
    srid: "27700",
    proj4: "+proj=tmerc +lat_0=49 +lon_0=-2 +k=0.9996012717 +x_0=400000 +y_0=-100000 +ellps=airy +towgs84=446.448,-125.157,542.06,0.15,0.247,0.842,-20.489 +units=m +no_defs",
};

describe("coordinate systems", () => {
    registerCoordinateSystems([GEOGRAPHIC, BRITISH_NATIONAL_GRID]);

    it("passes WGS84 positions through unchanged", () => {
        expect(toWgs84("4326", [-0.1276, 51.5072])).toEqual([-0.1276, 51.5072]);
        expect(fromWgs84("4326", [-0.1276, 51.5072])).toEqual([
            -0.1276, 51.5072,
        ]);
    });

    it("round-trips a position through a projected system", () => {
        const [easting, northing] = fromWgs84("27700", [-0.1276, 51.5072]);
        expect(easting).toBeCloseTo(530000, -3);
        expect(northing).toBeCloseTo(180000, -3);

        const [longitude, latitude] = toWgs84("27700", [easting, northing]);
        expect(longitude).toBeCloseTo(-0.1276, 6);
        expect(latitude).toBeCloseTo(51.5072, 6);
    });

    it("distinguishes geographic from projected systems", () => {
        expect(isGeographicCoordinateSystem(GEOGRAPHIC)).toBe(true);
        expect(isGeographicCoordinateSystem(BRITISH_NATIONAL_GRID)).toBe(false);
    });

    it("uses six decimal places for degrees and two for meters", () => {
        expect(getCoordinateDecimalPlaces(GEOGRAPHIC)).toBe(6);
        expect(getCoordinateDecimalPlaces(BRITISH_NATIONAL_GRID)).toBe(2);
        expect(getCoordinateDecimalPlaces(undefined)).toBe(6);
    });
});
