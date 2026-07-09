import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";

export interface ResourceInstanceReference {
    resourceId: string;
    ontologyProperty?: string;
    resourceXresourceId?: string;
    inverseOntologyProperty?: string;
}

export interface ResourceInstanceDataItem {
    display_value: string;
    order_field: number;
    resourceinstanceid: string;
}

export interface ResourceInstanceListOption {
    display_value: string;
    resource_id: string;
}

export interface ResourceInstanceListCardXNodeXWidgetData
    extends CardXNodeXWidgetData {
    node: CardXNodeXWidgetData["node"] & {
        config: {
            graphs?:
                | {
                      graphid: string;
                      name: string;
                  }[]
                | undefined;
        };
    };
}

export interface ResourceInstanceListAliasedNodeData extends AliasedNodeData {
    node_value: ResourceInstanceReference[] | null;
    details: ResourceInstanceListOption[];
}
