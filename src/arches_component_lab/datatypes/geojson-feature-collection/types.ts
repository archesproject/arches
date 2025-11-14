import type { AliasedNodeData } from "@/arches_component_lab/types.ts";
import type { FeatureCollection } from "geojson";

export interface GeoJSONFeatureCollectionValue extends AliasedNodeData {
    display_value: string;
    node_value: FeatureCollection | null;
    details: never[];
}
