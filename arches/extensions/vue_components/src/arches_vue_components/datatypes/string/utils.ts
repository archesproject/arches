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

export function resolveInitialLanguageCode(
    nodeValue: Record<string, LanguageValue> | null | undefined,
    requestedLanguageCode: string,
): string {
    const filledLanguageCodes = Object.entries(nodeValue ?? {})
        .filter(([, languageValue]) => languageValue.value !== "")
        .map(([languageCode]) => languageCode);
    if (filledLanguageCodes.includes(requestedLanguageCode)) {
        return requestedLanguageCode;
    }
    if (filledLanguageCodes.length > 0) {
        return filledLanguageCodes[0];
    }
    return requestedLanguageCode;
}
