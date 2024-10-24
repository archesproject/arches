import { describe, it, expect } from "vitest";
import generateArchesURL from "@/arches/utils/generate-arches-url.ts";

// @ts-expect-error  ARCHES_URLS is defined globally
global.ARCHES_URLS = {
    example_url: "/{language_code}/admin/example/{id}",
    another_url: "/admin/another/{id}",
    multi_interpolation_url:
        "/{language_code}/resource/{resource_id}/edit/{field_id}/version/{version_id}",
};

describe("generateArchesURL", () => {
    it("should return a valid URL with specified language code and parameters", () => {
        const result = generateArchesURL("example_url", { id: "123" }, "fr");
        expect(result).toBe("/fr/admin/example/123");
    });

    it("should use the <html> lang attribute when no language code is provided", () => {
        Object.defineProperty(document.documentElement, "lang", {
            value: "de",
            configurable: true,
        });

        const result = generateArchesURL("example_url", { id: "123" });
        expect(result).toBe("/de/admin/example/123");
    });

    it("should throw an error if the URL name is not found", () => {
        expect(() =>
            generateArchesURL("invalid_url", { id: "123" }, "fr"),
        ).toThrowError("Key 'invalid_url' not found in JSON object");
    });

    it("should replace URL parameters correctly", () => {
        const result = generateArchesURL("another_url", { id: "456" });
        expect(result).toBe("/admin/another/456");
    });

    it("should handle URLs without language code placeholder", () => {
        const result = generateArchesURL("another_url", { id: "789" });
        expect(result).toBe("/admin/another/789");
    });

    it("should handle multiple interpolations in the URL", () => {
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
});
