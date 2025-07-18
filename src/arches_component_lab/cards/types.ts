import type { NodeData } from "@/arches_component_lab/types.ts";

export interface AliasedTileData {
    aliased_data: {
        [key: string]: NodeData;
    };
    nodegroup: string;
    parenttile: string | null;
    provisionaledits: {
        [key: string]: NodeData;
    } | null;
    resourceinstance: string;
    sortorder: number;
    tileid: string;
}
