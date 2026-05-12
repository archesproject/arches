import arches from "arches";
import Cookies from "js-cookie";

import type { FeatureCollection } from "geojson";

import type { ResourceDescriptor } from "@/arches_component_lab/widgets/MapWidget/types.ts";

export async function fetchMapData(): Promise<Record<string, unknown>> {
    const response = await fetch(
        arches.urls["arches-component-lab-api-map-data"],
    );
    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message ?? response.statusText);
    return parsed;
}

export async function fetchDrawnFeaturesBuffer(
    features: FeatureCollection,
): Promise<FeatureCollection> {
    const response = await fetch(
        arches.urls["arches-component-lab-api-feature-buffer"],
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
    const response = await fetch(arches.urls.resource_descriptors + resourceId);
    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message ?? response.statusText);
    return parsed;
}

export async function fetchGeoJSONBounds(
    features: FeatureCollection,
): Promise<[number, number, number, number]> {
    const response = await fetch(
        arches.urls["arches-component-lab-api-geojson-bounds"],
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
