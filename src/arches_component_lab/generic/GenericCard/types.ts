import type { AliasedTileNodeValue } from "@/arches_component_lab/types.ts";

export interface AliasedTileData {
    aliased_data: {
        [key: string]: AliasedTileNodeValue;
    };
    nodegroup: string;
    parenttile: string | null;
    provisionaledits: {
        [key: string]: AliasedTileNodeValue;
    } | null;
    resourceinstance: string;
    sortorder: number;
    tileid: string;
}
