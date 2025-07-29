export interface AliasedNodeData {
    display_value: string;
    node_value: unknown;
    details: unknown[];
}

export type AliasedNodegroupData = AliasedTileData | AliasedTileData[] | null;

export interface AliasedData {
    [key: string]: AliasedNodeData | AliasedNodegroupData;
}

export interface AliasedTileData {
    aliased_data: AliasedData;
    nodegroup: string;
    parenttile: string | null;
    provisionaledits: AliasedData | null;
    resourceinstance: string;
    sortorder: number;
    tileid: string | null;
}

export interface CardXNodeXWidgetData {
    card: {
        name: string;
    };
    config: {
        defaultValue: unknown | null;
    };
    id: string;
    label: string;
    node: {
        alias: string;
        isrequired: boolean;
        nodeid: string;
    };
    sortorder: number;
    visible: boolean;
    widget: {
        component: string;
    };
}
