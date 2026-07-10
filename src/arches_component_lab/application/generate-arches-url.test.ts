import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { generateArchesURL } from "@/arches_component_lab/application/generate-arches-url.ts";

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
            invalid_type: "/not/array",
        };
    });

    afterEach(() => {
        document.documentElement.lang = originalLang;
    });

    it("returns a valid URL with specified language code and parameters", () => {
        const result = generateArchesURL(
            "example_url",
            { id: "123" },
            undefined,
            "fr",
        );
        expect(result).toBe("/fr/admin/example/123");
    });

    it("uses the <html> lang attribute when no language code is provided", () => {
        document.documentElement.lang = "de-DE";
        const result = generateArchesURL("example_url", { id: "123" });
        expect(result).toBe("/de/admin/example/123");
    });

    it("throws an error if the URL name is not found", () => {
        expect(() =>
            generateArchesURL(
                "non_existent_url",
                { id: "123" },
                undefined,
                "fr",
            ),
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
            undefined,
            "es",
        );
        expect(result).toBe("/es/resource/42/edit/name/version/7");
    });

    it("selects the exact candidate when available (candidate with all required parameters)", () => {
        const result = generateArchesURL(
            "candidate_test",
            { a: "1", b: "2" },
            undefined,
            "en",
        );
        expect(result).toBe("/en/test/1");
    });

    it("selects the first candidate when no exact match is available", () => {
        const result = generateArchesURL("no_exact_match", {
            id: "123",
            extra: "456",
        });
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
            undefined,
            "it",
        );
        expect(result).toBe("/it/repeated/555/again/555");
    });

    it("handles URLs with no placeholders", () => {
        const result = generateArchesURL("plain_url", {});
        expect(result).toBe("/plain/url");
    });

    it("ignores extra parameters not defined in the URL template", () => {
        const result = generateArchesURL(
            "extra_params",
            { id: "321", unused: "shouldBeIgnored" },
            undefined,
            "pt",
        );
        expect(result).toBe("/pt/extra/321");
    });

    it("appends query parameters to the URL", () => {
        const result = generateArchesURL(
            "example_url",
            { id: "123" },
            { page: "2", limit: "10" },
            "en",
        );
        expect(result).toBe("/en/admin/example/123?page=2&limit=10");
    });

    it("does not append a query string when queryParameters is not provided", () => {
        const result = generateArchesURL(
            "example_url",
            { id: "123" },
            undefined,
            "en",
        );
        expect(result).toBe("/en/admin/example/123");
    });

    it("does not append a query string when queryParameters is an empty object", () => {
        const result = generateArchesURL(
            "example_url",
            { id: "123" },
            {},
            "en",
        );
        expect(result).toBe("/en/admin/example/123");
    });
});
