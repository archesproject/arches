import type { Language } from "@/arches_vue_components/types.ts";
import type { LanguageAliasedNodeData } from "@/arches_vue_components/datatypes/language/types.ts";

export function buildLanguageAliasedNodeData(
    nodeValue: string | null,
    languages: Language[],
): LanguageAliasedNodeData {
    const language = languages.find((lang) => lang.code === nodeValue);
    return {
        node_value: nodeValue,
        display_value: language?.name ?? nodeValue ?? "",
        details: [],
    };
}
