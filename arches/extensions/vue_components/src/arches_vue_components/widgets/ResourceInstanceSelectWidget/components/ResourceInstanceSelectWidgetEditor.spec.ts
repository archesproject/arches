import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import OpenVue from "openvue/config";

import ResourceInstanceSelectWidgetEditor from "@/arches_vue_components/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetEditor.vue";

import type { VueWrapper } from "@vue/test-utils";
import type { ResourceInstanceCardXNodeXWidgetData } from "@/arches_vue_components/datatypes/resource-instance/types.ts";

const UNAVAILABLE_RESOURCE_ID = "unavailable-resource";
const READABLE_RESOURCE_ID = "readable-resource";

vi.mock("@/arches_vue_components/application/generate-arches-url.ts", () => ({
    generateArchesURL: (urlName: string) => urlName,
}));

vi.mock("@/arches_vue_components/datatypes/resource-instance/api.ts", () => ({
    fetchRelatableResources: () =>
        Promise.resolve({
            data: [
                {
                    resourceinstanceid: READABLE_RESOURCE_ID,
                    display_value: "Readable",
                },
            ],
            current_page: 1,
            total_results: 1,
        }),
}));

function makeWidget(): ResourceInstanceCardXNodeXWidgetData {
    return {
        card: {
            name: "Related",
            sortorder: 0,
            cardid: "related-card",
            nodegroup_id: "related-nodegroup",
            nodes: [],
            visible: true,
        },
        config: {},
        id: "related-widget",
        label: "Related",
        node: {
            alias: "related",
            isrequired: false,
            nodeid: "related-node",
            datatype: "resource-instance",
            config: {},
        },
        sortorder: 0,
        visible: true,
        widget: {
            widgetid: "resource-instance-select-widget",
            component: "ResourceInstanceSelectWidget",
        },
    };
}

function mountEditor(selectedResourceId: string): VueWrapper {
    return mount(ResourceInstanceSelectWidgetEditor, {
        props: {
            cardXNodeXWidgetData: makeWidget(),
            graphSlug: "graph",
            nodeAlias: "related",
            aliasedNodeData: {
                node_value: [{ resourceId: selectedResourceId }],
                display_value: "",
                details: [],
            },
        },
        global: { plugins: [[OpenVue, { theme: "none" }]] },
    });
}

describe("ResourceInstanceSelectWidgetEditor", () => {
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

    it("labels a selected resource missing from the results as unavailable", async () => {
        const wrapper = mountEditor(UNAVAILABLE_RESOURCE_ID);
        await flushPromises();

        expect(wrapper.text()).toContain("Unavailable resource");
    });
});
