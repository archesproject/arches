/// <reference types="geojson" />

type BBox = number[]
type Feature = GeoJSON.Feature<any> | GeoJSON.GeometryObject
type Features = GeoJSON.FeatureCollection<any> | GeoJSON.GeometryCollection

declare class RBush {
    insert(feature: Feature | BBox): RBush;
    load(features: Features | BBox[]): RBush;
    remove(feature: Feature | BBox, equals?: (a: Feature, b: Feature) => boolean): RBush;
    clear(): RBush;
    search(geojson: Feature | Features | BBox): Features;
    all(): Features;
    collides(geosjon: Feature | Features | BBox): boolean;
    toJSON(): any;
    fromJSON(data: any): RBush;
}

/**
 * https://github.com/mourner/rbush
 */
declare function rbush(maxEntries?: number): RBush;
declare namespace rbush {}
export = rbush;