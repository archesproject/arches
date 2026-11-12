import { describe, expect, it } from "vitest";

import {
    buildEmptyFileMetadata,
    getFileAltText,
    getVisibleMetadataFields,
    hasAnyAltText,
    setLocalizedValue,
    shouldShowMetadataLanguageSelect,
} from "@/arches_vue_components/datatypes/file-list/utils.ts";

import type { Language } from "@/arches_vue_components/types.ts";
import type {
    FileListCardXNodeXWidgetData,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types.ts";

const english: Language = {
    code: "en",
    default_direction: "ltr",
    id: 1,
    isdefault: true,
    name: "English",
    scope: "system",
};
const arabic: Language = {
    code: "ar",
    default_direction: "rtl",
    id: 2,
    isdefault: false,
    name: "Arabic",
    scope: "system",
};

function buildFileReference(
    overrides: Partial<FileReference> = {},
): FileReference {
    return {
        name: "IMG_0042.jpg",
        url: "/files/IMG_0042.jpg",
        ...overrides,
    } as FileReference;
}

describe("buildEmptyFileMetadata", () => {
    it("starts every metadata field with an empty value per language", () => {
        const metadata = buildEmptyFileMetadata([english, arabic]);

        for (const field of [
            "altText",
            "title",
            "description",
            "attribution",
        ] as const) {
            expect(metadata[field]).toEqual({
                en: { value: "", direction: "ltr" },
                ar: { value: "", direction: "rtl" },
            });
        }
    });

    it("gives each field its own object", () => {
        const metadata = buildEmptyFileMetadata([english]);

        expect(metadata.altText).not.toBe(metadata.title);
    });
});

describe("getVisibleMetadataFields", () => {
    function buildCardXNodeXWidgetData(
        metadataFields?: FileListCardXNodeXWidgetData["config"]["metadataFields"],
    ): FileListCardXNodeXWidgetData {
        return {
            config: { metadataFields },
        } as FileListCardXNodeXWidgetData;
    }

    it("shows every field without widget data", () => {
        expect(getVisibleMetadataFields(undefined)).toEqual([
            "altText",
            "title",
            "description",
            "attribution",
        ]);
    });

    it("shows every field when the config has no entries", () => {
        expect(
            getVisibleMetadataFields(buildCardXNodeXWidgetData()),
        ).toHaveLength(4);
    });

    it("hides only the fields whose visible bit is false", () => {
        const cardXNodeXWidgetData = buildCardXNodeXWidgetData({
            title: { visible: false },
            description: { visible: false },
            attribution: { visible: true },
        });

        expect(getVisibleMetadataFields(cardXNodeXWidgetData)).toEqual([
            "altText",
            "attribution",
        ]);
    });
});

describe("shouldShowMetadataLanguageSelect", () => {
    function buildCardXNodeXWidgetData(
        metadataLanguageSelect?: FileListCardXNodeXWidgetData["config"]["metadataLanguageSelect"],
    ): FileListCardXNodeXWidgetData {
        return {
            config: { metadataLanguageSelect },
        } as FileListCardXNodeXWidgetData;
    }

    it("hides the picker without widget data or a config entry", () => {
        expect(shouldShowMetadataLanguageSelect(undefined)).toBe(false);
        expect(
            shouldShowMetadataLanguageSelect(buildCardXNodeXWidgetData()),
        ).toBe(false);
    });

    it("follows the visible bit", () => {
        expect(
            shouldShowMetadataLanguageSelect(
                buildCardXNodeXWidgetData({ visible: true }),
            ),
        ).toBe(true);
        expect(
            shouldShowMetadataLanguageSelect(
                buildCardXNodeXWidgetData({ visible: false }),
            ),
        ).toBe(false);
    });
});

describe("getFileAltText", () => {
    it("reads the alt text in the requested language", () => {
        const fileReference = buildFileReference({
            altText: {
                en: { value: "A red vase", direction: "ltr" },
                ar: { value: "مزهرية حمراء", direction: "rtl" },
            },
        });

        expect(getFileAltText(fileReference, "ar")).toBe("مزهرية حمراء");
    });

    it("falls back to the title in the same language", () => {
        const fileReference = buildFileReference({
            altText: { en: { value: "", direction: "ltr" } },
            title: { en: { value: "Vase, 1890", direction: "ltr" } },
        });

        expect(getFileAltText(fileReference, "en")).toBe("Vase, 1890");
    });

    it("never falls back to the file name", () => {
        expect(getFileAltText(buildFileReference(), "en")).toBe("");
    });

    it("returns an empty string without a language", () => {
        const fileReference = buildFileReference({
            altText: { en: { value: "A red vase", direction: "ltr" } },
        });

        expect(getFileAltText(fileReference, null)).toBe("");
    });
});

describe("hasAnyAltText", () => {
    it("is true when any language has alt text", () => {
        const fileReference = buildFileReference({
            altText: {
                en: { value: "", direction: "ltr" },
                ar: { value: "مزهرية", direction: "rtl" },
            },
        });

        expect(hasAnyAltText(fileReference)).toBe(true);
    });

    it("ignores whitespace-only values", () => {
        const fileReference = buildFileReference({
            altText: { en: { value: "  ", direction: "ltr" } },
        });

        expect(hasAnyAltText(fileReference)).toBe(false);
    });
});

describe("setLocalizedValue", () => {
    it("sets one language and keeps the others", () => {
        const updated = setLocalizedValue(
            { en: { value: "A vase", direction: "ltr" } },
            arabic,
            "مزهرية",
        );

        expect(updated).toEqual({
            en: { value: "A vase", direction: "ltr" },
            ar: { value: "مزهرية", direction: "rtl" },
        });
    });
});
