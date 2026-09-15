import type {
    LanguageValue,
    StringAliasedNodeData,
} from "@/arches_vue_components/datatypes/string/types.ts";

export function buildStringAliasedNodeData(
    nodeValue: Record<string, LanguageValue> | null,
    activeLangCode: string,
): StringAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue?.[activeLangCode]?.value ?? "",
        details: [],
    };
}
