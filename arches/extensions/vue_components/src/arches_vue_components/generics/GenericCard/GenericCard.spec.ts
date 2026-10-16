import { defineComponent, h, onMounted } from "vue";
import { createPinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { flushPromises, mount } from "@vue/test-utils";
import OpenVue from "openvue/config";

import GenericCard from "@/arches_vue_components/generics/GenericCard/GenericCard.vue";

import { fetchTileData } from "@/arches_vue_components/generics/GenericCard/api.ts";
import { EDIT } from "@/arches_vue_components/widgets/constants.ts";

import type { Component } from "vue";
import type { VueWrapper } from "@vue/test-utils";
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

vi.mock("@/arches_vue_components/application/generate-arches-url.ts", () => ({
    generateArchesURL: (urlName: string) => urlName,
}));

vi.mock("@/arches_vue_components/generics/GenericCard/api.ts", () => ({
    fetchTileData: vi.fn(() => Promise.resolve(TILE)),
}));

function stubFetch(areLanguagesAvailable: boolean): void {
    vi.stubGlobal(
        "fetch",
        vi.fn((url: string) => {
            if (!url.includes("languages")) {
                return Promise.resolve(new Response(JSON.stringify([WIDGET])));
            }
            if (!areLanguagesAvailable) {
                return Promise.resolve(
                    new Response(JSON.stringify({ message: "Offline" }), {
                        status: 503,
                    }),
                );
            }
            return Promise.resolve(
                new Response(
                    JSON.stringify({ languages: [], request_language: "en" }),
                ),
            );
        }),
    );
}

function mountCard(
    props: Record<string, unknown>,
    editorStub: Component | boolean = true,
): VueWrapper {
    return mount(GenericCard, {
        props: {
            mode: EDIT,
            graphSlug: "pigment",
            nodegroupAlias: "names",
            ...props,
        },
        global: {
            plugins: [createPinia(), [OpenVue, { theme: "none" }]],
            stubs: { GenericCardEditor: editorStub },
        },
    });
}

describe("GenericCard", () => {
    beforeEach(() => {
        stubFetch(true);
    });

    it("still renders its editor when the languages cannot be preloaded", async () => {
        stubFetch(false);
        const wrapper = mountCard({ tileData: TILE });
        await flushPromises();

        expect(
            wrapper.findComponent({ name: "GenericCardEditor" }).exists(),
        ).toBe(true);
    });

    it("fetches the new tile when its tileId changes in edit mode", async () => {
        const wrapper = mountCard({ tileId: "smalt" });
        await flushPromises();

        await wrapper.setProps({ tileId: "cobalt" });
        await flushPromises();

        expect(vi.mocked(fetchTileData)).toHaveBeenLastCalledWith(
            "pigment",
            "names",
            "cobalt",
        );
    });

    it("keeps its editor mounted when the tile data it was given changes", async () => {
        let editorMountCount = 0;
        const GenericCardEditorStub = defineComponent({
            name: "GenericCardEditor",
            setup() {
                onMounted(() => {
                    editorMountCount += 1;
                });
                return () => h("form");
            },
        });
        const wrapper = mountCard({ tileData: TILE }, GenericCardEditorStub);
        await flushPromises();

        await wrapper.setProps({ tileData: { ...TILE } });
        await flushPromises();

        expect(editorMountCount).toBe(1);
    });
});
