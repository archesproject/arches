import type { AliasedTileNodeValue } from "@/arches_component_lab/types.ts";

export interface NonLocalizedTextValue extends AliasedTileNodeValue {
    display_value: string;
    node_value: string;
    details: never[];
}
