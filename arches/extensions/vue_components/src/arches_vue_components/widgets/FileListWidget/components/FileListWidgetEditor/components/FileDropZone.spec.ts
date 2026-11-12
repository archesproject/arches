import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import OpenVue from "openvue/config";
import Tooltip from "openvue/tooltip";

import FileDropZone from "@/arches_vue_components/widgets/FileListWidget/components/FileListWidgetEditor/components/FileDropZone.vue";

function mountFileDropZone(isDisabled: boolean) {
    const openFileChooser = vi.fn();
    const wrapper = mount(FileDropZone, {
        global: {
            plugins: [OpenVue],
            directives: { tooltip: Tooltip },
            mocks: { $gettext: (text: string) => text },
        },
        props: { openFileChooser, isDisabled, acceptedFileTypes: [] },
    });
    return { wrapper, openFileChooser };
}

describe("FileDropZone", () => {
    it("is a real button that opens the file chooser", async () => {
        const { wrapper, openFileChooser } = mountFileDropZone(false);
        const button = wrapper.get("button");

        expect(button.attributes("type")).toBe("button");
        await button.trigger("click");

        expect(openFileChooser).toHaveBeenCalledOnce();
    });

    it("explains why it is disabled and doesn't open the chooser", async () => {
        const { wrapper, openFileChooser } = mountFileDropZone(true);
        const button = wrapper.get("button");

        expect(button.attributes("aria-disabled")).toBe("true");
        const reasonId = button.attributes("aria-describedby");
        expect(wrapper.get(`#${reasonId}`).text()).toBe(
            "Maximum number of files reached.",
        );

        await button.trigger("click");
        expect(openFileChooser).not.toHaveBeenCalled();
    });
});
