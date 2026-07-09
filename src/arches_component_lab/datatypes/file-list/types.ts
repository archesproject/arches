import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";

export interface FileReference {
    url: string;
    name: string;
    path: string;
    size: number;
    type: string;
    index: number;
    width: number;
    height: number;
    status: string;
    content: string;
    file_id: string;
    accepted: boolean;
    lastModified: number;
    altText: string;
    attribution: string;
    description: string;
    title: string;
}
export interface FileListCardXNodeXWidgetData extends CardXNodeXWidgetData {
    config: CardXNodeXWidgetData["config"] & {
        acceptedFiles: string;
        maxFiles: number;
        maxFilesize: number;
        rerender: boolean;
        label: string;
    };
}

export interface FileListAliasedNodeData extends AliasedNodeData {
    node_value: FileReference[] | null;
    details: never[];
}
