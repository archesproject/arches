import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type {
    FileListAliasedNodeData,
    FileListCardXNodeXWidgetData,
    FileMetadata,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types.ts";

export interface FileData extends Partial<FileMetadata> {
    name: string;
    size: number;
    type: string;
    url: string;
    file: File;
    node_id: string;
}

export type OpenVueFile = File & { objectURL: string };

export interface FileListWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: FileListCardXNodeXWidgetData;
    aliasedNodeData?: FileListAliasedNodeData | null;
    value?: FileReference[] | null;
    // Off by default: metadata is edited in the request language, as in the
    // Knockout widget. Turn on to let editors pick a language per file.
    shouldShowMetadataLanguageSelect?: boolean;
}
