import { defineComponent, onMounted } from "vue";
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

function makeTile(nameType: string | null): AliasedTileData {
    return {
        aliased_data: {
            name_content: nodeData("Smalt"),
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
});
