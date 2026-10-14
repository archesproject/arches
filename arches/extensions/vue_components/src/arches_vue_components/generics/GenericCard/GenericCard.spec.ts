import { describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import OpenVue from "openvue/config";

import GenericCard from "@/arches_vue_components/generics/GenericCard/GenericCard.vue";

import { EDIT } from "@/arches_vue_components/widgets/constants.ts";

import type {
    AliasedTileData,
    CardXNodeXWidgetData,
} from "@/arches_vue_components/types.ts";

const WIDGET: CardXNodeXWidgetData = {
    card: {
        name: "Names",
        sortorder: 0,
        cardid: "names-card",
        nodegroup_id: "names-nodegroup",
        nodes: [],
        visible: true,
    },
    config: {},
    id: "name-content-widget",
    label: "Name",
    node: {
        alias: "name_content",
        isrequired: false,
        nodeid: "name-content-node",
        datatype: "string",
        config: {},
    },
    sortorder: 0,
    visible: true,
    widget: { widgetid: "text-widget", component: "TextWidget" },
};

const TILE: AliasedTileData = {
    aliased_data: {
        name_content: { display_value: "", node_value: null, details: [] },
    },
    nodegroup: "names-nodegroup",
    parenttile: null,
    provisionaledits: null,
    resourceinstance: "resource",
    sortorder: 0,
    tileid: "tile",
};

vi.mock(
    "@/arches_vue_components/stores/useNodegroupWidgetConfigStore.ts",
    () => ({
        useNodegroupWidgetConfigStore: () => ({
            fetchNodegroupWidgetConfigs: () => Promise.resolve([WIDGET]),
        }),
    }),
);

vi.mock("@/arches_vue_components/stores/useLanguageStore.ts", () => ({
    useLanguageStore: () => ({
        fetchAllLanguages: () => Promise.reject(new Error("Offline")),
    }),
}));

describe("GenericCard", () => {
    it("still renders its editor when the languages cannot be preloaded", async () => {
        const wrapper = mount(GenericCard, {
            props: {
                mode: EDIT,
                graphSlug: "pigment",
                nodegroupAlias: "names",
                tileData: TILE,
            },
            global: {
                plugins: [[OpenVue, { theme: "none" }]],
                stubs: { GenericCardEditor: true },
            },
        });
        await flushPromises();

        expect(
            wrapper.findComponent({ name: "GenericCardEditor" }).exists(),
        ).toBe(true);
        expect(wrapper.text()).not.toContain("Offline");
    });
});
