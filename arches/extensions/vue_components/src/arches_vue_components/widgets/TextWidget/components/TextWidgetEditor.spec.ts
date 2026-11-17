import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import { createPinia } from "pinia";
import OpenVue from "openvue/config";
import Select from "openvue/select";

import TextWidgetEditor from "@/arches_vue_components/widgets/TextWidget/components/TextWidgetEditor.vue";

import type { Language } from "@/arches_vue_components/types.ts";

const { ENGLISH, FRENCH } = vi.hoisted(
    (): { ENGLISH: Language; FRENCH: Language } => ({
        ENGLISH: {
            code: "en",
            default_direction: "ltr",
            id: 1,
            isdefault: true,
            name: "English",
            scope: "system",
        },
        FRENCH: {
            code: "fr",
            default_direction: "ltr",
            id: 2,
            isdefault: false,
            name: "French",
            scope: "system",
        },
    }),
);

vi.mock("@/arches_vue_components/widgets/api.ts", () => ({
    fetchLanguages: () =>
        Promise.resolve({
            languages: [ENGLISH, FRENCH],
            request_language: ENGLISH.code,
        }),
}));

describe("TextWidgetEditor", () => {
    beforeEach(() => {
        vi.stubGlobal(
            "matchMedia",
            vi.fn().mockReturnValue({
                matches: false,
                addEventListener: vi.fn(),
                removeEventListener: vi.fn(),
            }),
        );
    });

    it("reports a language switch without editing the value", async () => {
        const wrapper = mount(TextWidgetEditor, {
            props: {
                aliasedNodeData: {
                    node_value: {
                        en: { value: "Barcelona", direction: "ltr" },
                    },
                    display_value: "Barcelona",
                    details: [],
                },
            },
            global: {
                plugins: [createPinia(), [OpenVue, { theme: "none" }]],
            },
        });
        await flushPromises();

        wrapper.findComponent(Select).vm.$emit("update:modelValue", FRENCH);
        await flushPromises();

        expect(wrapper.emitted("update:selectedLanguage")).toEqual([
            [ENGLISH.code],
            [FRENCH.code],
        ]);
        expect(wrapper.emitted("update:aliasedNodeData")).toBeUndefined();
    });
});
