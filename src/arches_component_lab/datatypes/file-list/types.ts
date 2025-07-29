import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

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

export interface FileListValue extends AliasedNodeData {
    display_value: string;
    node_value: FileReference[];
    details: never[];
}
