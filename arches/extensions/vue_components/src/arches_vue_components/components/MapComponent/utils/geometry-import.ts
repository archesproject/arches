import geojsonhint from "@mapbox/geojsonhint/geojsonhint.js";
import { kml } from "@tmcw/togeojson";
import shp from "shpjs";

import type { Feature, FeatureCollection, GeoJSON } from "geojson";

export const ACCEPTED_GEOMETRY_FILE_EXTENSIONS = [
    "zip",
    "shp",
    "json",
    "geojson",
    "kml",
];

export type GeometryImportErrorCode =
    | "unsupported-file-type"
    | "parse-failed"
    | "no-features";

export class GeometryImportError extends Error {
    code: GeometryImportErrorCode;

    constructor(code: GeometryImportErrorCode) {
        super(code);
        this.code = code;
    }
}

interface GeoJsonHint {
    level?: string;
    line?: number;
    message: string;
}

export function findGeoJsonErrors(text: string): GeoJsonHint[] {
    const hints: GeoJsonHint[] = geojsonhint.hint(text);
    return hints.filter((hint) => hint.level !== "message");
}

function toFeatureCollection(geojson: GeoJSON): FeatureCollection {
    if (geojson.type === "FeatureCollection") {
        return geojson;
    }
    if (geojson.type === "Feature") {
        return { type: "FeatureCollection", features: [geojson] };
    }
    return {
        type: "FeatureCollection",
        features: [{ type: "Feature", properties: {}, geometry: geojson }],
    };
}

function asCollections(
    parsed: FeatureCollection | FeatureCollection[],
): FeatureCollection[] {
    return Array.isArray(parsed) ? parsed : [parsed];
}

async function parseFeatureCollections(
    file: File,
    extension: string,
): Promise<FeatureCollection[]> {
    if (extension === "zip") {
        return asCollections(await shp(await file.arrayBuffer()));
    }
    if (extension === "shp") {
        return asCollections(await shp({ shp: await file.arrayBuffer() }));
    }

    const text = await file.text();

    if (extension === "kml") {
        return [kml(new DOMParser().parseFromString(text, "text/xml"))];
    }
    if (findGeoJsonErrors(text).length) {
        throw new GeometryImportError("parse-failed");
    }
    return [toFeatureCollection(JSON.parse(text))];
}

export async function parseGeometryFile(file: File): Promise<Feature[]> {
    const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
    if (!ACCEPTED_GEOMETRY_FILE_EXTENSIONS.includes(extension)) {
        throw new GeometryImportError("unsupported-file-type");
    }

    let collections: FeatureCollection[];
    try {
        collections = await parseFeatureCollections(file, extension);
    } catch {
        throw new GeometryImportError("parse-failed");
    }

    const features = collections
        .flatMap((collection) => collection.features)
        .filter((feature) => feature.geometry !== null);

    if (!features.length) {
        throw new GeometryImportError("no-features");
    }
    return features;
}
