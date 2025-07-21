import type { AliasedTileNodeValue } from "@/arches_component_lab/types.ts";

export interface URLValue extends AliasedTileNodeValue {
    display_value: string;
    node_value: {
        url: string;
        url_label: string;
    };
    details: never[];
}
