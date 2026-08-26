import type { FeatureCollection } from "geojson";
import type { GeoJSONFeatureCollectionAliasedNodeData } from "@/arches_vue_components/datatypes/geojson-feature-collection/types.ts";

export function buildGeoJSONFeatureCollectionAliasedNodeData(
    nodeValue: FeatureCollection | null,
): GeoJSONFeatureCollectionAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue ? JSON.stringify(nodeValue) : "",
        details: [],
    };
}
