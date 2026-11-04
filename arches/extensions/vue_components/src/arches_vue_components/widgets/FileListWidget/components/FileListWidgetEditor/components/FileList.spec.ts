import { mount } from "@vue/test-utils";
import { beforeAll, describe, expect, it, vi } from "vitest";

import OpenVue from "openvue/config";

import FileList from "@/arches_vue_components/widgets/FileListWidget/components/FileListWidgetEditor/components/FileList.vue";

import type { Language } from "@/arches_vue_components/types.ts";
import type { FileReference } from "@/arches_vue_components/datatypes/file-list/types.ts";

const { interpolateGettext } = vi.hoisted(() => ({
    interpolateGettext: (text: string, params?: Record<string, string>) =>
        text.replace(
            /%\{(\w+)\}/g,
            (_match, key: string) => params?.[key] ?? "",
        ),
}));

// The global setup's useGettext mock doesn't interpolate, and FileList
// builds its error message in the script.
vi.mock("vue3-gettext", () => ({
    useGettext: () => ({ $gettext: interpolateGettext }),
}));

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

function mountFileList(
    fileReference: Partial<FileReference>,
    extraProps: Record<string, unknown> = {},
) {
    return mount(FileList, {
        global: {
            plugins: [OpenVue],
            mocks: { $gettext: interpolateGettext },
        },
        props: {
            files: [
                {
                    name: "vase.jpg",
                    url: "/files/vase.jpg",
                    file_id: "file-1",
                    ...fileReference,
                } as FileReference,
            ],
            languages: [english, arabic],
            defaultMetadataLanguage: english,
            isAltTextRequired: true,
            ...extraProps,
        },
    });
}

describe("FileList metadata", () => {
    beforeAll(() => {
        // OpenVue's Select listens for orientation changes on mount.
        vi.stubGlobal(
            "matchMedia",
            vi.fn().mockReturnValue({
                matches: false,
                addEventListener: vi.fn(),
                removeEventListener: vi.fn(),
            }),
        );
    });

    it("labels every metadata input", () => {
        const wrapper = mountFileList({});

        for (const input of wrapper.findAll("input, textarea")) {
            const label = wrapper.find(
                `label[for="${input.attributes("id")}"]`,
            );
            expect(label.exists()).toBe(true);
        }
    });

    it("marks alt text required and links its help text", () => {
        const wrapper = mountFileList({});
        const altTextInput = wrapper.get('input[aria-required="true"]');
        const helpId = altTextInput.attributes("aria-describedby");

        expect(wrapper.get(`#${helpId}`).text()).toContain(
            "Describe the image",
        );
        expect(altTextInput.attributes("aria-invalid")).toBeUndefined();
    });

    it("shows a linked error once empty alt text loses focus", async () => {
        const wrapper = mountFileList({});
        const altTextInput = wrapper.get('input[aria-required="true"]');

        await altTextInput.trigger("blur");

        expect(altTextInput.attributes("aria-invalid")).toBe("true");
        const describedByIds = altTextInput
            .attributes("aria-describedby")!
            .split(" ");
        expect(wrapper.get(`#${describedByIds[1]}`).text()).toBe(
            "Enter alternative text for vase.jpg.",
        );
    });

    it("shows no error when another language has alt text", async () => {
        const wrapper = mountFileList({
            altText: { fr: { value: "Un vase", direction: "ltr" } },
        });
        const altTextInput = wrapper.get('input[aria-required="true"]');

        await altTextInput.trigger("blur");

        expect(altTextInput.attributes("aria-invalid")).toBeUndefined();
    });

    it("tags the inputs with the metadata language", () => {
        const wrapper = mountFileList({});

        for (const input of wrapper.findAll("input, textarea")) {
            expect(input.attributes("lang")).toBe("en");
            expect(input.attributes("dir")).toBe("ltr");
        }
    });

    it("emits the localized value when alt text is typed", async () => {
        const wrapper = mountFileList({});

        await wrapper.get('input[aria-required="true"]').setValue("A vase");

        expect(wrapper.emitted("update:metadata")?.[0]).toEqual([
            0,
            "altText",
            { en: { value: "A vase", direction: "ltr" } },
        ]);
    });

    it("names the remove button after the file", () => {
        const wrapper = mountFileList({});

        expect(wrapper.get(".delete-button").attributes("aria-label")).toBe(
            "Remove vase.jpg",
        );
    });

    it("uses the alt text, not the file name, for the thumbnail", () => {
        const wrapper = mountFileList({});

        expect(wrapper.get("img").attributes("alt")).toBe("");
    });

    it("hides the language select by default", () => {
        const wrapper = mountFileList({});

        expect(wrapper.find(".file-metadata-language").exists()).toBe(false);
    });

    it("edits the selected language when the language select is on", async () => {
        const wrapper = mountFileList({}, { shouldShowLanguageSelect: true });
        const languageSelect = wrapper.findComponent({ name: "Select" });

        expect(languageSelect.props("modelValue")).toBe("en");
        languageSelect.vm.$emit("update:modelValue", "ar");
        await wrapper.vm.$nextTick();

        const altTextInput = wrapper.get('input[aria-required="true"]');
        expect(altTextInput.attributes("lang")).toBe("ar");
        expect(altTextInput.attributes("dir")).toBe("rtl");

        await altTextInput.setValue("مزهرية");
        expect(wrapper.emitted("update:metadata")?.[0]?.[2]).toEqual({
            ar: { value: "مزهرية", direction: "rtl" },
        });
    });

    it("collapses the additional metadata behind a toggle", async () => {
        const wrapper = mountFileList({});
        const toggle = wrapper.get(".additional-metadata-toggle");
        const drawer = wrapper.get(`#${toggle.attributes("aria-controls")}`);

        expect(toggle.attributes("aria-expanded")).toBe("false");
        expect(drawer.isVisible()).toBe(false);

        await toggle.trigger("click");

        expect(toggle.attributes("aria-expanded")).toBe("true");
        expect(drawer.isVisible()).toBe(true);
    });

    it("shows only the visible metadata fields", () => {
        const wrapper = mountFileList(
            {},
            { visibleMetadataFields: ["altText", "attribution"] },
        );
        const labels = wrapper.findAll("label").map((label) => label.text());

        expect(labels).toEqual(["Alternative text (required)", "Attribution"]);
    });

    it("drops the toggle when no additional fields are visible", () => {
        const wrapper = mountFileList(
            {},
            { visibleMetadataFields: ["altText"] },
        );

        expect(wrapper.find(".additional-metadata-toggle").exists()).toBe(
            false,
        );
    });
});
