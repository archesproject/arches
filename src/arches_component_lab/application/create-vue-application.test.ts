import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { defineComponent } from "vue";
import { createVueApplication } from "@/arches_component_lab/application/create-vue-application";

vi.mock("vue3-gettext", () => ({
    useGettext: () => ({ $gettext: (text: string) => text }),
    createGettext: () => ({ install: vi.fn() }),
}));

const MockComponent = defineComponent({ template: "<div />" });

const mockI18nData = {
    enabled_languages: { en: "English" },
    language: "en",
    translations: {},
};

describe("createVueApplication", () => {
    beforeEach(() => {
        // @ts-expect-error ARCHES_URLS is defined globally
        global.ARCHES_URLS = {
            "arches:get_frontend_i18n_data": [
                { url: "/i18n/data", params: [] },
            ],
        };

        global.fetch = vi.fn().mockResolvedValue({
            ok: true,
            json: () => Promise.resolve(mockI18nData),
        } as Response);

        vi.stubGlobal(
            "matchMedia",
            vi.fn().mockReturnValue({ matches: false }),
        );
        localStorage.clear();
    });

    afterEach(() => {
        vi.restoreAllMocks();
        document.documentElement.classList.remove("arches-dark");
    });

    it("returns a Vue App instance", async () => {
        const app = await createVueApplication({ component: MockComponent });
        expect(app).toBeDefined();
        expect(typeof app.mount).toBe("function");
    });

    it("throws when the fetch response is not ok", async () => {
        global.fetch = vi.fn().mockResolvedValue({
            ok: false,
            statusText: "Not Found",
        } as Response);

        await expect(
            createVueApplication({ component: MockComponent }),
        ).rejects.toThrow("Not Found");
    });

    it('adds dark mode class when localStorage is "true"', async () => {
        localStorage.setItem("arches.arches-dark", "true");
        await createVueApplication({ component: MockComponent });
        expect(document.documentElement.classList.contains("arches-dark")).toBe(
            true,
        );
    });

    it('does not add dark mode class when localStorage is "false"', async () => {
        localStorage.setItem("arches.arches-dark", "false");
        await createVueApplication({ component: MockComponent });
        expect(document.documentElement.classList.contains("arches-dark")).toBe(
            false,
        );
    });

    it("adds dark mode class when localStorage is null and system prefers dark", async () => {
        vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: true }));
        await createVueApplication({ component: MockComponent });
        expect(document.documentElement.classList.contains("arches-dark")).toBe(
            true,
        );
    });

    it("does not add dark mode class when localStorage is null and system prefers light", async () => {
        await createVueApplication({ component: MockComponent });
        expect(document.documentElement.classList.contains("arches-dark")).toBe(
            false,
        );
    });
});
