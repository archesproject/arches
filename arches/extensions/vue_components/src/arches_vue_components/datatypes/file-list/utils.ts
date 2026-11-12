import { FILE_METADATA_FIELDS } from "@/arches_vue_components/datatypes/file-list/constants.ts";

import type { Language } from "@/arches_vue_components/types.ts";
import type { LanguageValue } from "@/arches_vue_components/datatypes/string/types.ts";
import type {
    FileListAliasedNodeData,
    FileListCardXNodeXWidgetData,
    FileMetadata,
    FileMetadataField,
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

export function buildEmptyFileMetadata(languages: Language[]): FileMetadata {
    const buildEmptyLocalizedValue = () =>
        Object.fromEntries(
            languages.map((language) => [
                language.code,
                { value: "", direction: language.default_direction },
            ]),
        );

    return Object.fromEntries(
        FILE_METADATA_FIELDS.map((field) => [
            field,
            buildEmptyLocalizedValue(),
        ]),
    ) as FileMetadata;
}

export function getVisibleMetadataFields(
    cardXNodeXWidgetData: FileListCardXNodeXWidgetData | undefined,
): FileMetadataField[] {
    const metadataFieldConfigs = cardXNodeXWidgetData?.config.metadataFields;
    return FILE_METADATA_FIELDS.filter(
        (field) => metadataFieldConfigs?.[field]?.visible !== false,
    );
}

export function shouldShowMetadataLanguageSelect(
    cardXNodeXWidgetData: FileListCardXNodeXWidgetData | undefined,
): boolean {
    return (
        cardXNodeXWidgetData?.config.metadataLanguageSelect?.visible === true
    );
}

export function getLocalizedValue(
    localizedValue: Record<string, LanguageValue> | undefined,
    languageCode: string | null,
): string {
    if (!languageCode) {
        return "";
    }
    return localizedValue?.[languageCode]?.value ?? "";
}

export function getFileAltText(
    fileReference: FileReference,
    languageCode: string | null,
): string {
    return (
        getLocalizedValue(fileReference.altText, languageCode) ||
        getLocalizedValue(fileReference.title, languageCode)
    );
}

export function hasAnyAltText(fileReference: FileReference): boolean {
    return Object.values(fileReference.altText ?? {}).some((languageValue) =>
        languageValue.value.trim(),
    );
}

export function setLocalizedValue(
    localizedValue: Record<string, LanguageValue> | undefined,
    language: Language,
    value: string,
): Record<string, LanguageValue> {
    return {
        ...localizedValue,
        [language.code]: { value, direction: language.default_direction },
    };
}
