import type { NodeData } from "@/arches_component_lab/types.ts";

export interface NonLocalizedTextData extends NodeData {
    display_value: string;
    node_value: string;
    details: never[];
}
