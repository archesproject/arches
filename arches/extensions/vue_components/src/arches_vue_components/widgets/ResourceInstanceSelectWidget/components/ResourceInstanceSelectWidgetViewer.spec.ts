import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";

import ResourceInstanceSelectWidgetViewer from "@/arches_vue_components/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetViewer.vue";

vi.mock("@/arches_vue_components/application/generate-arches-url.ts", () => ({
    generateArchesURL: (urlName: string) => urlName,
}));

describe("ResourceInstanceSelectWidgetViewer", () => {
    it("links to a related resource that has a name", () => {
        const wrapper = mount(ResourceInstanceSelectWidgetViewer, {
            props: {
                aliasedNodeData: {
                    node_value: [{ resourceId: "readable-resource" }],
                    display_value: "Readable",
                    details: [],
                },
            },
        });

        expect(wrapper.find("a").text()).toBe("Readable");
    });

    it("renders no link when the related resource has no name to show", () => {
        const wrapper = mount(ResourceInstanceSelectWidgetViewer, {
            props: {
                aliasedNodeData: {
                    node_value: [{ resourceId: "unavailable-resource" }],
                    display_value: "",
                    details: [],
                },
            },
        });

        expect(wrapper.find("a").exists()).toBe(false);
    });
});
