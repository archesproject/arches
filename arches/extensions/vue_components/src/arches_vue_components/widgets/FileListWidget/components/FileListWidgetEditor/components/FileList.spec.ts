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

    it("labels every metadata input and language select", () => {
        const wrapper = mountFileList({});

        for (const input of wrapper.findAll("input, textarea")) {
            const label = wrapper.find(
                `label[for="${input.attributes("id")}"]`,
            );
            expect(label.exists()).toBe(true);
        }
        expect(wrapper.find('[aria-label="Language for Title"]').exists()).toBe(
            true,
        );
    });

    it("links alt text help, then a required error once it loses focus empty", async () => {
        const wrapper = mountFileList({});
        const altTextInput = wrapper.get('input[aria-required="true"]');
        const [helpId] = altTextInput
            .attributes("aria-describedby")!
            .split(" ");

        expect(wrapper.get(`#${helpId}`).text()).toContain(
            "Describe the image",
        );
        expect(altTextInput.attributes("aria-invalid")).toBeUndefined();

        await altTextInput.trigger("blur");

        expect(altTextInput.attributes("aria-invalid")).toBe("true");
        const [, errorId] = altTextInput
            .attributes("aria-describedby")!
            .split(" ");
        expect(wrapper.get(`#${errorId}`).text()).toBe(
            "Enter alternative text for vase.jpg.",
        );
    });

    it("defaults each field to the system language", () => {
        const wrapper = mountFileList({});

        const languageSelects = wrapper.findAllComponents({ name: "Select" });
        expect(languageSelects).toHaveLength(4);
        for (const languageSelect of languageSelects) {
            expect(languageSelect.props("modelValue")).toBe("en");
        }
        for (const input of wrapper.findAll("input, textarea")) {
            expect(input.attributes("lang")).toBe("en");
            expect(input.attributes("dir")).toBe("ltr");
        }
    });

    it("switches one field's language without affecting the others", async () => {
        const wrapper = mountFileList({
            altText: { en: { value: "A vase", direction: "ltr" } },
        });
        const [altTextSelect, titleSelect] = wrapper.findAllComponents({
            name: "Select",
        });

        altTextSelect.vm.$emit("update:modelValue", "ar");
        await wrapper.vm.$nextTick();

        expect(titleSelect.props("modelValue")).toBe("en");
        const altTextInput = wrapper.get('input[aria-required="true"]');
        expect(altTextInput.attributes("lang")).toBe("ar");
        expect(altTextInput.attributes("dir")).toBe("rtl");
        expect((altTextInput.element as HTMLInputElement).value).toBe("");

        await altTextInput.setValue("مزهرية");
        expect(wrapper.emitted("update:metadata")?.[0]).toEqual([
            0,
            "altText",
            {
                en: { value: "A vase", direction: "ltr" },
                ar: { value: "مزهرية", direction: "rtl" },
            },
        ]);
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

    it("omits hidden metadata fields", () => {
        const wrapper = mountFileList(
            {},
            { hiddenMetadataFields: ["title", "description"] },
        );
        const labels = wrapper
            .findAll(".file-metadata-label")
            .map((label) => label.text());

        expect(labels).toEqual(["Alternative text (required)", "Attribution"]);
    });

    it("drops the additional metadata toggle when every additional field is hidden", () => {
        const wrapper = mountFileList(
            {},
            { hiddenMetadataFields: ["title", "description", "attribution"] },
        );

        expect(wrapper.find(".additional-metadata-toggle").exists()).toBe(
            false,
        );
    });
});
