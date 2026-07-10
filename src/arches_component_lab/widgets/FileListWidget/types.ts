import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type {
    FileListAliasedNodeData,
    FileListCardXNodeXWidgetData,
    FileReference,
} from "@/arches_component_lab/datatypes/file-list/types.ts";

export interface FileData {
    name: string;
    size: number;
    type: string;
    url: string;
    file: File;
    node_id: string;
}

export type PrimeVueFile = File & { objectURL: string };

export interface FileListWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: FileListCardXNodeXWidgetData;
    aliasedNodeData?: FileListAliasedNodeData | null;
    value?: FileReference[] | null;
}
