import type {
    FileListAliasedNodeData,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types.ts";

export function buildFileListAliasedNodeData(
    nodeValue: FileReference[] | null,
): FileListAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue?.map((file) => file.name).join(", ") ?? "",
        details: [],
    };
}
