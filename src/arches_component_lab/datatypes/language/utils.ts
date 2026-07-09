import type { Language } from "@/arches_component_lab/types.ts";
import type { LanguageAliasedNodeData } from "@/arches_component_lab/datatypes/language/types.ts";

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
