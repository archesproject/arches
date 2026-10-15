import { defineComponent, nextTick, onMounted } from "vue";
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";
import OpenVue from "openvue/config";

import GenericCardEditor from "@/arches_vue_components/generics/GenericCard/components/GenericCardEditor.vue";

import type {
    AliasedNodeData,
    AliasedTileData,
    CardXNodeXWidgetData,
} from "@/arches_vue_components/types.ts";

const mountedNodeAliases: string[] = [];

const GenericWidgetStub = defineComponent({
    name: "GenericWidget",
    props: {
        nodeAlias: { type: String, required: true },
        aliasedNodeData: { type: Object, default: null },
    },
    setup(props) {
        onMounted(() => mountedNodeAliases.push(props.nodeAlias));
    },
    template: "<div class='widget-stub' />",
});

function makeWidget(nodeAlias: string): CardXNodeXWidgetData {
    return {
        card: {
            name: "Names",
            sortorder: 0,
            cardid: "names-card",
            nodegroup_id: "names-nodegroup",
            nodes: [],
            visible: true,
        },
        config: {},
        id: `${nodeAlias}-widget`,
        label: nodeAlias,
        node: {
            alias: nodeAlias,
            isrequired: false,
            nodeid: `${nodeAlias}-node`,
            datatype: "string",
            config: {},
        },
        sortorder: 0,
        visible: true,
        widget: { widgetid: "text-widget", component: "TextWidget" },
    };
}

function nodeData(value: string | null): AliasedNodeData {
    return { display_value: value ?? "", node_value: value, details: [] };
}

function makeTile(
    nameType: string | null,
    nameContent = "Smalt",
): AliasedTileData {
    return {
        aliased_data: {
            name_content: nodeData(nameContent),
            name_type: nodeData(nameType),
        },
        nodegroup: "names-nodegroup",
        parenttile: null,
        provisionaledits: null,
        resourceinstance: "resource",
        sortorder: 0,
        tileid: "smalt",
    };
}

describe("GenericCardEditor", () => {
    it("rebuilds only the fields changed from outside the form", async () => {
        const wrapper = mount(GenericCardEditor, {
            props: {
                cardXNodeXWidgetData: [
                    makeWidget("name_content"),
                    makeWidget("name_type"),
                ],
                graphSlug: "pigment",
                nodegroupAlias: "names",
                resourceInstanceId: "resource",
                shouldShowFormButtons: false,
                tileData: makeTile("Primary"),
            },
            global: {
                plugins: [[OpenVue, { theme: "none" }]],
                stubs: { GenericWidget: GenericWidgetStub },
            },
        });
        mountedNodeAliases.length = 0;

        await wrapper.setProps({ tileData: makeTile("Primary") });
        expect(mountedNodeAliases).toEqual([]);

        await wrapper.setProps({ tileData: makeTile(null) });
        expect(mountedNodeAliases).toEqual(["name_type"]);
        expect(
            wrapper
                .findAllComponents(GenericWidgetStub)
                .find((widget) => widget.props("nodeAlias") === "name_type")
                ?.props("aliasedNodeData").node_value,
        ).toBeNull();
    });

    it("cancels back to values pushed from outside, not to echoed edits", async () => {
        const wrapper = mount(GenericCardEditor, {
            props: {
                cardXNodeXWidgetData: [
                    makeWidget("name_content"),
                    makeWidget("name_type"),
                ],
                graphSlug: "pigment",
                nodegroupAlias: "names",
                resourceInstanceId: "resource",
                tileData: makeTile("Primary"),
            },
            global: {
                plugins: [[OpenVue, { theme: "none" }]],
                stubs: { GenericWidget: GenericWidgetStub },
            },
        });
        const nameTypeWidget = wrapper
            .findAllComponents(GenericWidgetStub)
            .find((widget) => widget.props("nodeAlias") === "name_type");
        if (nameTypeWidget === undefined) {
            throw new Error("No name_type widget");
        }

        nameTypeWidget.vm.$emit("update:aliasedNodeData", nodeData("Typed"));
        nameTypeWidget.vm.$emit("update:isDirty", true);
        await wrapper.setProps({ tileData: makeTile("Typed") });
        await wrapper.setProps({ tileData: makeTile("Typed", "Cobalt") });

        const cancelButton = wrapper
            .findAll("button")
            .find((button) => button.text() === "Cancel");
        if (cancelButton === undefined) {
            throw new Error("No Cancel button");
        }
        await cancelButton.trigger("click");
        await nextTick();

        const [[resetNodeData]] = wrapper.emitted("reset") as [
            [Record<string, AliasedNodeData>],
        ];
        expect(resetNodeData.name_content.node_value).toBe("Cobalt");
        expect(resetNodeData.name_type.node_value).toBe("Primary");
    });
});
