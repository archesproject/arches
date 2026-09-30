import type { AliasedNodeData } from "@/arches_vue_components/types.ts";
import type { FeatureCollection } from "geojson";

export interface GeoJSONFeatureCollectionAliasedNodeData
    extends AliasedNodeData {
    node_value: FeatureCollection | null;
    details: never[];
}
