import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { generateArchesURL } from "@/arches/utils/generate-arches-url.ts";

const originalLang = document.documentElement.lang;

describe("generateArchesURL", () => {
    beforeEach(() => {
        // @ts-expect-error ARCHES_URLS is defined globally
        global.ARCHES_URLS = {
            example_url: [
                {
                    url: "/{language_code}/admin/example/{id}",
                    params: ["language_code", "id"],
                },
            ],
            another_url: [{ url: "/admin/another/{id}", params: ["id"] }],
            multi_interpolation_url: [
                {
                    url: "/{language_code}/resource/{resource_id}/edit/{field_id}/version/{version_id}",
                    params: [
                        "language_code",
                        "resource_id",
                        "field_id",
                        "version_id",
                    ],
                },
            ],
            candidate_test: [
                {
                    url: "/{language_code}/test/{a}",
                    params: ["language_code", "a", "b"],
                },
                {
                    url: "/{language_code}/test/{a}",
                    params: ["language_code", "a"],
                },
            ],
            no_exact_match: [
                { url: "/test/{id}", params: ["id"] },
                { url: "/test/alt/{id}", params: ["id"] },
            ],
            missing_required: [
                {
                    url: "/required/{id}/value/{value}",
                    params: ["id", "value"],
                },
            ],
            duplicate_interpolation: [
                {
                    url: "/{language_code}/repeated/{id}/again/{id}",
                    params: ["language_code", "id"],
                },
            ],
            plain_url: [{ url: "/plain/url", params: [] }],
            extra_params: [
                {
                    url: "/{language_code}/extra/{id}",
                    params: ["language_code", "id"],
                },
            ],
            invalid_type: "/not/array", // This should trigger an error due to type.
        };
    });

    afterEach(() => {
        document.documentElement.lang = originalLang;
    });

    it("returns a valid URL with specified language code and parameters", () => {
        const result = generateArchesURL("example_url", { id: "123" }, "fr");
        expect(result).toBe("/fr/admin/example/123");
    });

    it("uses the <html> lang attribute when no language code is provided", () => {
        // Set the language on the html element to a specific value.
        document.documentElement.lang = "de-DE";
        const result = generateArchesURL("example_url", { id: "123" });
        // It will take 'de' (splitting at '-') from "de-DE"
        expect(result).toBe("/de/admin/example/123");
    });

    it("throws an error if the URL name is not found", () => {
        expect(() =>
            generateArchesURL("non_existent_url", { id: "123" }, "fr"),
        ).toThrowError("Key 'non_existent_url' not found in JSON object");
    });

    it("throws an error if the global route is not an array", () => {
        expect(() =>
            generateArchesURL("invalid_type", { id: "999" }),
        ).toThrowError("Key 'invalid_type' not found in JSON object");
    });

    it("replaces URL parameters correctly", () => {
        const result = generateArchesURL("another_url", { id: "456" });
        expect(result).toBe("/admin/another/456");
    });

    it("handles URLs without a language code placeholder", () => {
        const result = generateArchesURL("another_url", { id: "789" });
        expect(result).toBe("/admin/another/789");
    });

    it("handles multiple interpolations in the URL", () => {
        const result = generateArchesURL(
            "multi_interpolation_url",
            {
                resource_id: "42",
                field_id: "name",
                version_id: "7",
            },
            "es",
        );
        expect(result).toBe("/es/resource/42/edit/name/version/7");
    });

    it("selects the exact candidate when available (candidate with all required parameters)", () => {
        // In candidate_test the first candidate requires ["a", "b"] while the second requires only ["a"].
        // Given both "a" and "b" are provided, the first candidate (length 2) is an exact match.
        const result = generateArchesURL(
            "candidate_test",
            { a: "1", b: "2" },
            "en",
        );
        expect(result).toBe("/en/test/1");
    });

    it("selects the first candidate when no exact match is available", () => {
        // In no_exact_match both candidates require only ["id"].
        // However, if we provide an extra parameter, neither candidate is an exact match (candidate params count 1 vs. provided 2).
        // The function falls back to taking the first candidate.
        const result = generateArchesURL("no_exact_match", {
            id: "123",
            extra: "456",
        });
        // Both candidates replace {id} the same way; by default, the first candidate is chosen.
        expect(result).toBe("/test/123");
    });

    it("throws an error when required URL parameters are missing", () => {
        expect(() =>
            generateArchesURL("missing_required", { id: "123" }),
        ).toThrowError(/No matching URL pattern for 'missing_required'/);
    });

    it("replaces duplicate interpolation keys correctly", () => {
        const result = generateArchesURL(
            "duplicate_interpolation",
            { id: "555" },
            "it",
        );
        expect(result).toBe("/it/repeated/555/again/555");
    });

    it("handles URLs with no placeholders", () => {
        const result = generateArchesURL("plain_url", {});
        expect(result).toBe("/plain/url");
    });

    it("ignores extra parameters not defined in the URL template", () => {
        // extra_params has only {id} to replace. Any additional parameter (like "unused") is ignored.
        const result = generateArchesURL(
            "extra_params",
            { id: "321", unused: "shouldBeIgnored" },
            "pt",
        );
        expect(result).toBe("/pt/extra/321");
    });
});
