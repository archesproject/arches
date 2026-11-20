import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import OpenVue from "openvue/config";

import FileListWidgetViewer from "@/arches_vue_components/widgets/FileListWidget/components/FileListWidgetViewer.vue";

import type {
    FileListAliasedNodeData,
    FileReference,
} from "@/arches_vue_components/datatypes/file-list/types.ts";

vi.mock("@/arches_vue_components/stores/useSettingsStore.ts", () => ({
    useSettingsStore: () => ({
        fetchForceScriptName: () => Promise.resolve(""),
    }),
}));

vi.mock("@/arches_vue_components/stores/useLanguageStore.ts", () => ({
    useLanguageStore: () => ({
        requestLanguageCode: "en",
        fetchAllLanguages: () => Promise.resolve([]),
    }),
}));

function fileReference(name: string, type: string): FileReference {
    return { name, type, url: `/files/${name}` } as FileReference;
}

describe("FileListWidgetViewer", () => {
    it("shows images in the gallery and lists other files as links", async () => {
        const wrapper = mount(FileListWidgetViewer, {
            props: {
                aliasedNodeData: {
                    display_value: "",
                    node_value: [
                        fileReference("pigment.jpg", "image/jpeg"),
                        fileReference("analysis.pdf", ""),
                    ],
                    details: [],
                } as unknown as FileListAliasedNodeData,
            },
            global: { plugins: [[OpenVue, { theme: "none" }]] },
        });
        await flushPromises();

        expect(
            wrapper.findComponent({ name: "Galleria" }).props("value"),
        ).toHaveLength(1);
        const fileLinks = wrapper.findAll(".file-list-viewer-file");
        expect(fileLinks).toHaveLength(1);
        expect(fileLinks[0].attributes("href")).toBe("/files/analysis.pdf");
        expect(fileLinks[0].text()).toBe("analysis.pdf");
    });
});
