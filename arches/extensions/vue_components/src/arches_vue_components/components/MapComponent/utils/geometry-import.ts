import { getIssues } from "@placemarkio/check-geojson";
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
    reason?: string;

    constructor(code: GeometryImportErrorCode, reason?: string) {
        super(code);
        this.code = code;
        this.reason = reason;
    }
}

export interface GeoJsonIssue {
    line?: number;
    message: string;
}

export function findGeoJsonIssues(text: string): GeoJsonIssue[] {
    return getIssues(text).map((issue) => ({
        line: text.slice(0, issue.from).split("\n").length,
        message: issue.message,
    }));
}

export async function parseGeometryFile(file: File): Promise<Feature[]> {
    const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
    if (!ACCEPTED_GEOMETRY_FILE_EXTENSIONS.includes(extension)) {
        throw new GeometryImportError("unsupported-file-type");
    }

    let features: Feature[];
    try {
        features = await readFeatures(file, extension);
    } catch (error) {
        if (error instanceof Error) {
            throw new GeometryImportError("parse-failed", error.message);
        }
        throw new GeometryImportError("parse-failed");
    }

    const featuresWithGeometry = features.filter(
        (feature) => feature.geometry !== null,
    );
    if (!featuresWithGeometry.length) {
        throw new GeometryImportError("no-features");
    }
    return featuresWithGeometry;
}

async function readFeatures(file: File, extension: string): Promise<Feature[]> {
    if (extension === "zip") {
        return featuresFromShapefile(await shp(await file.arrayBuffer()));
    }
    if (extension === "shp") {
        return featuresFromShapefile(
            await shp({ shp: await file.arrayBuffer() }),
        );
    }

    const text = await file.text();
    if (extension === "kml") {
        return kml(new DOMParser().parseFromString(text, "text/xml")).features;
    }

    const [firstIssue] = findGeoJsonIssues(text);
    if (firstIssue) {
        throw new Error(firstIssue.message);
    }
    return featuresFromGeoJson(JSON.parse(text));
}

function featuresFromShapefile(
    parsed: FeatureCollection | FeatureCollection[],
): Feature[] {
    return [parsed].flat().flatMap((collection) => collection.features);
}

function featuresFromGeoJson(geojson: GeoJSON): Feature[] {
    if (geojson.type === "FeatureCollection") {
        return geojson.features;
    }
    if (geojson.type === "Feature") {
        return [geojson];
    }
    return [{ type: "Feature", properties: {}, geometry: geojson }];
}
