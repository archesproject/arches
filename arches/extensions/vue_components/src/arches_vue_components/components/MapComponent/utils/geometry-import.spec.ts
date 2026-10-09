import { describe, expect, it } from "vitest";

import {
    GeometryImportError,
    parseGeometryFile,
} from "@/arches_vue_components/components/MapComponent/utils/geometry-import.ts";

function buildFile(name: string, contents: string): File {
    const file = new File([contents], name);
    Object.defineProperty(file, "text", {
        value: () => Promise.resolve(contents),
    });
    return file;
}

async function captureImportError(file: File): Promise<GeometryImportError> {
    try {
        await parseGeometryFile(file);
    } catch (error) {
        if (error instanceof GeometryImportError) {
            return error;
        }
    }
    throw new Error("Expected a GeometryImportError");
}

describe("parseGeometryFile", () => {
    it("reads a GeoJSON feature collection", async () => {
        const features = await parseGeometryFile(
            buildFile(
                "shapes.geojson",
                JSON.stringify({
                    type: "FeatureCollection",
                    features: [
                        {
                            type: "Feature",
                            properties: {},
                            geometry: { type: "Point", coordinates: [1, 2] },
                        },
                    ],
                }),
            ),
        );
        expect(features).toHaveLength(1);
        expect(features[0].geometry).toEqual({
            type: "Point",
            coordinates: [1, 2],
        });
    });

    it("wraps a bare geometry in a feature", async () => {
        const features = await parseGeometryFile(
            buildFile(
                "line.json",
                JSON.stringify({
                    type: "LineString",
                    coordinates: [
                        [0, 0],
                        [1, 1],
                    ],
                }),
            ),
        );
        expect(features[0].type).toBe("Feature");
        expect(features[0].geometry.type).toBe("LineString");
    });

    it("reads a KML placemark", async () => {
        const features = await parseGeometryFile(
            buildFile(
                "place.kml",
                `<?xml version="1.0" encoding="UTF-8"?>
                <kml xmlns="http://www.opengis.net/kml/2.2"><Document><Placemark>
                <Point><coordinates>-0.1276,51.5072</coordinates></Point>
                </Placemark></Document></kml>`,
            ),
        );
        expect(features[0].geometry).toEqual({
            type: "Point",
            coordinates: [-0.1276, 51.5072],
        });
    });

    it("rejects unsupported file types", async () => {
        const error = await captureImportError(buildFile("notes.txt", "hello"));
        expect(error.code).toBe("unsupported-file-type");
    });

    it("rejects invalid GeoJSON", async () => {
        const error = await captureImportError(
            buildFile("broken.json", "{ not json"),
        );
        expect(error.code).toBe("parse-failed");
        expect(error.reason).not.toBe("");
    });

    it("rejects files without features", async () => {
        const error = await captureImportError(
            buildFile(
                "empty.geojson",
                JSON.stringify({ type: "FeatureCollection", features: [] }),
            ),
        );
        expect(error.code).toBe("no-features");
    });
});
