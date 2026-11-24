import { describe, expect, it } from "vitest";

import {
    getFileAltText,
    hasAnyAltText,
} from "@/arches_vue_components/datatypes/file-list/utils.ts";

import type { FileReference } from "@/arches_vue_components/datatypes/file-list/types.ts";

function buildFileReference(
    overrides: Partial<FileReference> = {},
): FileReference {
    return {
        name: "IMG_0042.jpg",
        url: "/files/IMG_0042.jpg",
        ...overrides,
    } as FileReference;
}

describe("getFileAltText", () => {
    it("uses alt text, then title, in the requested language, never the file name", () => {
        const withAltText = buildFileReference({
            altText: {
                en: { value: "A red vase", direction: "ltr" },
                ar: { value: "مزهرية حمراء", direction: "rtl" },
            },
        });
        const withTitleOnly = buildFileReference({
            altText: { en: { value: "", direction: "ltr" } },
            title: { en: { value: "Vase, 1890", direction: "ltr" } },
        });

        expect(getFileAltText(withAltText, "ar")).toBe("مزهرية حمراء");
        expect(getFileAltText(withTitleOnly, "en")).toBe("Vase, 1890");
        expect(getFileAltText(withAltText, null)).toBe("");
        expect(getFileAltText(buildFileReference(), "en")).toBe("");
    });
});

describe("hasAnyAltText", () => {
    it("is true when any language has non-blank alt text", () => {
        const withArabicAltText = buildFileReference({
            altText: {
                en: { value: "  ", direction: "ltr" },
                ar: { value: "مزهرية", direction: "rtl" },
            },
        });
        const withBlankAltText = buildFileReference({
            altText: { en: { value: "  ", direction: "ltr" } },
        });

        expect(hasAnyAltText(withArabicAltText)).toBe(true);
        expect(hasAnyAltText(withBlankAltText)).toBe(false);
    });
});
