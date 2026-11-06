import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import OpenVue from "openvue/config";
import MultiSelect from "openvue/multiselect";

import ResourceInstanceMultiselectWidgetEditor from "@/arches_vue_components/widgets/ResourceInstanceMultiselectWidget/components/ResourceInstanceMultiselectWidgetEditor.vue";

import type { VueWrapper } from "@vue/test-utils";
import type {
    ResourceInstanceListAliasedNodeData,
    ResourceInstanceListCardXNodeXWidgetData,
    ResourceInstanceReference,
} from "@/arches_vue_components/datatypes/resource-instance-list/types.ts";

const UNAVAILABLE_RESOURCE_ID = "unavailable-resource";
const READABLE_RESOURCE_ID = "readable-resource";
const OTHER_RESOURCE_ID = "other-resource";

const UNAVAILABLE_REFERENCE: ResourceInstanceReference = {
    resourceId: UNAVAILABLE_RESOURCE_ID,
    relationship: "unavailable-relationship",
    inverseRelationship: "",
    resourceXresourceId: "unavailable-resource-x-resource",
};
const READABLE_REFERENCE: ResourceInstanceReference = {
    resourceId: READABLE_RESOURCE_ID,
    relationship: "readable-relationship",
    inverseRelationship: "readable-inverse-relationship",
    resourceXresourceId: "readable-resource-x-resource",
};

vi.mock("@/arches_vue_components/application/generate-arches-url.ts", () => ({
    generateArchesURL: (urlName: string) => urlName,
}));

vi.mock(
    "@/arches_vue_components/datatypes/resource-instance-list/api.ts",
    () => ({
        fetchRelatableResources: () =>
            Promise.resolve({
                data: [
                    {
                        resourceinstanceid: READABLE_RESOURCE_ID,
                        display_value: "Readable",
                    },
                    {
                        resourceinstanceid: OTHER_RESOURCE_ID,
                        display_value: "Other",
                    },
                ],
                current_page: 1,
                total_results: 2,
            }),
    }),
);

function makeWidget(): ResourceInstanceListCardXNodeXWidgetData {
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
            datatype: "resource-instance-list",
            config: {},
        },
        sortorder: 0,
        visible: true,
        widget: {
            widgetid: "resource-instance-multiselect-widget",
            component: "ResourceInstanceMultiselectWidget",
        },
    };
}

function mountEditor(): VueWrapper {
    return mount(ResourceInstanceMultiselectWidgetEditor, {
        props: {
            cardXNodeXWidgetData: makeWidget(),
            graphSlug: "graph",
            nodeAlias: "related",
            aliasedNodeData: {
                node_value: [UNAVAILABLE_REFERENCE, READABLE_REFERENCE],
                display_value: "Readable",
                details: [
                    {
                        resource_id: READABLE_RESOURCE_ID,
                        display_value: "Readable",
                    },
                ],
            },
        },
        global: { plugins: [[OpenVue, { theme: "none" }]] },
    });
}

function getLastEmittedNodeValue(
    wrapper: VueWrapper,
): ResourceInstanceReference[] | null {
    const emittedValues = wrapper.emitted("update:aliasedNodeData") as [
        ResourceInstanceListAliasedNodeData,
    ][];
    return emittedValues[emittedValues.length - 1][0].node_value;
}

function getChipLabels(wrapper: VueWrapper): string[] {
    return wrapper.findAll(".chip-text").map((chipText) => chipText.text());
}

describe("ResourceInstanceMultiselectWidgetEditor", () => {
    it("labels a selected resource missing from the results as unavailable", async () => {
        const wrapper = mountEditor();
        await flushPromises();

        expect(getChipLabels(wrapper)).toEqual([
            "Unavailable resource",
            "Readable",
        ]);
        const [unavailableChipButtons, readableChipButtons] =
            wrapper.findAll(".button-container");
        expect(unavailableChipButtons.findAll("a")).toHaveLength(0);
        expect(readableChipButtons.findAll("a")).toHaveLength(2);
    });

    it("keeps unavailable references when the selection is replaced", async () => {
        const wrapper = mountEditor();
        await flushPromises();

        wrapper
            .findComponent(MultiSelect)
            .vm.$emit("update:modelValue", [
                READABLE_RESOURCE_ID,
                OTHER_RESOURCE_ID,
            ]);

        expect(getLastEmittedNodeValue(wrapper)).toEqual([
            UNAVAILABLE_REFERENCE,
            READABLE_REFERENCE,
            {
                inverseRelationship: "",
                relationship: "",
                resourceId: OTHER_RESOURCE_ID,
                resourceXresourceId: "",
            },
        ]);
    });

    it("keeps unavailable references when everything is deselected", async () => {
        const wrapper = mountEditor();
        await flushPromises();

        wrapper.findComponent(MultiSelect).vm.$emit("update:modelValue", []);

        expect(getLastEmittedNodeValue(wrapper)).toEqual([
            UNAVAILABLE_REFERENCE,
        ]);
    });

    it("removes an unavailable reference through its own remove button", async () => {
        const wrapper = mountEditor();
        await flushPromises();

        const [unavailableChipButtons] = wrapper.findAll(".button-container");
        await unavailableChipButtons.find("button").trigger("click");

        expect(getLastEmittedNodeValue(wrapper)).toEqual([READABLE_REFERENCE]);
    });
});
