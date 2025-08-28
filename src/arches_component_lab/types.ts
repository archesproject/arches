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
    provisionaledits: object | null;
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
        placeholder?: string;
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
        widgetid: string;
        component: string;
    };
}

export interface StringCardXNodeXWidgetData extends CardXNodeXWidgetData {
    config: CardXNodeXWidgetData["config"] & {
        maxLength: string | null;
        placeholder: string | null;
    };
}

export interface ConceptRadioCardXNodeXWidgetData extends CardXNodeXWidgetData {
    config: CardXNodeXWidgetData["config"] & {
        groupDirection: string | null;
    };
}

export interface Language {
    code: string;
    default_direction: "ltr" | "rtl";
    id: number;
    isdefault: boolean;
    name: string;
    scope: string;
}
