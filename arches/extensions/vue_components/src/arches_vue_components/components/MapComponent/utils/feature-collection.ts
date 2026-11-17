import type { FeatureCollection, Geometry } from "geojson";

export function geometriesToFeatureCollection(
    geometries: Geometry[],
): FeatureCollection {
    return {
        type: "FeatureCollection",
        features: geometries.map((geometry) => ({
            type: "Feature",
            properties: {},
            geometry,
        })),
    };
}
