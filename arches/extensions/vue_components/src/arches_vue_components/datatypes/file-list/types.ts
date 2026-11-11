import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_vue_components/types.ts";
import type { LanguageValue } from "@/arches_vue_components/datatypes/string/types.ts";
import type { FILE_METADATA_FIELDS } from "@/arches_vue_components/datatypes/file-list/constants.ts";

export type FileMetadataField = (typeof FILE_METADATA_FIELDS)[number];
export type FileMetadata = Record<
    FileMetadataField,
    Record<string, LanguageValue>
>;

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
    altText?: Record<string, LanguageValue>;
    attribution?: Record<string, LanguageValue>;
    description?: Record<string, LanguageValue>;
    title?: Record<string, LanguageValue>;
}
// Mirrors CardXNodeXWidgetData.visible: a field is shown unless its
// `visible` bit is false. Saved widget configs have no entry, so every
// field is shown by default.
export interface FileMetadataFieldConfig {
    visible: boolean;
}

export interface FileListCardXNodeXWidgetData extends CardXNodeXWidgetData {
    config: CardXNodeXWidgetData["config"] & {
        acceptedFiles: string;
        maxFiles: number;
        maxFilesize: number;
        rerender: boolean;
        label: string;
        metadataFields?: Partial<
            Record<FileMetadataField, FileMetadataFieldConfig>
        >;
    };
}

export interface FileListAliasedNodeData extends AliasedNodeData {
    node_value: FileReference[] | null;
    details: never[];
}
