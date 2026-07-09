import type { FeatureCollection } from "geojson";
import type { GeoJSONFeatureCollectionAliasedNodeData } from "@/arches_component_lab/datatypes/geojson-feature-collection/types.ts";

export function buildGeoJSONFeatureCollectionAliasedNodeData(
    nodeValue: FeatureCollection | null,
): GeoJSONFeatureCollectionAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: "",
        details: [],
    };
}
