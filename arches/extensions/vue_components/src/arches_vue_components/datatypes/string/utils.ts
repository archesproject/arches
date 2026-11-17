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

export function getOnlyFilledLanguageCode(
    nodeValue: Record<string, LanguageValue> | null | undefined,
): string | undefined {
    const filledLanguageCodes = Object.entries(nodeValue ?? {})
        .filter(([, languageValue]) => languageValue.value !== "")
        .map(([languageCode]) => languageCode);
    if (filledLanguageCodes.length === 1) {
        return filledLanguageCodes[0];
    }
    return undefined;
}
