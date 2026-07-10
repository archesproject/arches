import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type {
    FileListAliasedNodeData,
    FileListCardXNodeXWidgetData,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types.ts";

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
