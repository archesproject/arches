import { describe, it, expect } from "vitest";
import generateArchesURL from "@/arches/utils/generate-arches-url.ts";

// @ts-expect-error  ARCHES_URLS is defined globally
global.ARCHES_URLS = {
    example_url: "/admin/{language_code}/example/{id}",
    another_url: "/admin/another/{id}",
};

describe("generateArchesURL", () => {
    it("should return a valid URL with language code and parameters", () => {
        const result = generateArchesURL("example_url", "fr", { id: "123" });
        expect(result).toBe("/admin/fr/example/123");
    });

    it("should use the <html> lang attribute when no language code is provided", () => {
        Object.defineProperty(document.documentElement, "lang", {
            value: "de",
            configurable: true,
        });

        const result = generateArchesURL("example_url", null, { id: "123" });
        expect(result).toBe("/admin/de/example/123");
    });

    it("should throw an error if the URL name is not found", () => {
        expect(() =>
            generateArchesURL("invalid_url", "fr", { id: "123" }),
        ).toThrowError("Key 'invalid_url' not found in JSON object");
    });

    it("should replace URL parameters correctly", () => {
        const result = generateArchesURL("another_url", null, { id: "456" });
        expect(result).toBe("/admin/another/456");
    });

    it("should handle missing language code and parameter placeholders", () => {
        const result = generateArchesURL("another_url", "es", { id: "789" });

        console.log(result);
        expect(result).toBe("/admin/another/789");
    });
});
