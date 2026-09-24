import Cookies from "js-cookie";

import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

import type { FeatureCollection } from "geojson";

import type { ResourceDescriptor } from "@/arches_vue_components/components/MapComponent/types.ts";

export async function fetchMapData(): Promise<Record<string, unknown>> {
    const response = await fetch(
        generateArchesURL("arches_vue_components:api-map-data"),
    );
    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message ?? response.statusText);
    return parsed;
}

export async function fetchDrawnFeaturesBuffer(
    features: FeatureCollection,
): Promise<FeatureCollection> {
    const response = await fetch(
        generateArchesURL("arches_vue_components:api-feature-buffer"),
        {
            method: "POST",
            headers: { "X-CSRFTOKEN": Cookies.get("csrftoken") as string },
            body: JSON.stringify({ features }),
        },
    );
    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message ?? response.statusText);
    return parsed;
}

export async function fetchResourceDescriptor(
    resourceId: string,
): Promise<ResourceDescriptor> {
    const response = await fetch(
        generateArchesURL("arches:resource_descriptors", {
            resourceid: resourceId,
        }),
    );
    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message ?? response.statusText);
    return parsed;
}

export async function fetchGeoJSONBounds(
    features: FeatureCollection,
): Promise<[number, number, number, number]> {
    const response = await fetch(
        generateArchesURL("arches_vue_components:api-geojson-bounds"),
        {
            method: "POST",
            headers: { "X-CSRFTOKEN": Cookies.get("csrftoken") as string },
            body: JSON.stringify(features),
        },
    );
    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message ?? response.statusText);
    return parsed;
}
