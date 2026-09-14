import {
    ALT_LABEL,
    HIDDEN_LABEL,
    PREF_LABEL,
} from "@/arches_controlled_lists/constants.ts";
import {
    getItemLabel,
    rankLabel,
    reorderItems,
} from "@/arches_controlled_lists/utils.ts";
import { controlled_lists } from "../../../tests/fixtures/data/sample_list_api_response.json";

import type { Label } from "@/arches_controlled_lists/types";

// Test utils
function asLabel(valuetype_id: string, language_id: string): Label {
    return {
        value: "arbitrary",
        valuetype_id,
        language_id,
    };
}

const systemLanguageCode = "en-ZA"; // arbitrary
const emptyLabel = {
    value: "",
    language_id: "",
    valuetype_id: "",
};

describe("rankLabel() util", () => {
    const rank = (
        valuetype_id: string,
        labelLanguageCode: string,
        desiredLanguageCode: string,
    ) =>
        rankLabel(
            asLabel(valuetype_id, labelLanguageCode),
            desiredLanguageCode,
            systemLanguageCode,
        );

    // Test cases inspired from python module
    it("Prefers explicit region", () => {
        expect(rank(PREF_LABEL, "fr-CA", "fr-CA")).toBeGreaterThan(
            rank(PREF_LABEL, "fr", "fr-CA"),
        );
    });
    it("Prefers pref over alt", () => {
        expect(rank(PREF_LABEL, "fr", "fr-CA")).toBeGreaterThan(
            rank(ALT_LABEL, "fr", "fr-CA"),
        );
    });
    it("Prefers alt over hidden", () => {
        expect(rank(ALT_LABEL, "fr", "fr-CA")).toBeGreaterThan(
            rank(HIDDEN_LABEL, "fr", "fr-CA"),
        );
    });
    it("Prefers alt label in system language to anything else", () => {
        expect(rank(ALT_LABEL, systemLanguageCode, "en")).toBeGreaterThan(
            rank(PREF_LABEL, "de", "en"),
        );
    });
    it("Prefers region-insensitive match in system language", () => {
        expect(rank(PREF_LABEL, "en", "de")).toBeGreaterThan(
            rank(PREF_LABEL, "fr", "de"),
        );
    });
});

describe("getItemLabel() util", () => {
    it("Returns empty label if no labels to search", () => {
        expect(
            getItemLabel(
                { labels: [] },
                systemLanguageCode,
                systemLanguageCode,
            ),
        ).toEqual(emptyLabel);
        expect(
            getItemLabel(
                { values: [] },
                systemLanguageCode,
                systemLanguageCode,
            ),
        ).toEqual(emptyLabel);
    });
    it("Falls back to system language", () => {
        expect(
            getItemLabel(
                {
                    labels: [
                        asLabel(PREF_LABEL, "de"),
                        asLabel(PREF_LABEL, systemLanguageCode),
                    ],
                },
                "fr",
                systemLanguageCode,
            ).language_id,
        ).toEqual(systemLanguageCode);
    });
});

describe("reorderItems() util", () => {
    it("reorders a set of siblings from 0", () => {
        reorderItems(
            controlled_lists[0],
            controlled_lists[0].items[0],
            controlled_lists[0].items,
            false,
        );
        expect(controlled_lists[0].items.map((item) => item.sortorder)).toEqual(
            [0, 1],
        );
        expect(
            controlled_lists[0].items[0].children.map(
                (child) => child.sortorder,
            ),
        ).toEqual([0]);
        expect(
            controlled_lists[0].items[1].children.map(
                (child) => child.sortorder,
            ),
        ).toEqual([0]);
    });
});
