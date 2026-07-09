import type {
    FileListAliasedNodeData,
    FileReference,
} from "@/arches_component_lab/datatypes/file-list/types.ts";

export function buildFileListAliasedNodeData(
    nodeValue: FileReference[] | null,
): FileListAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue?.map((file) => file.name).join(", ") ?? "",
        details: [],
    };
}
