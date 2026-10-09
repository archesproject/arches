import { ref } from "vue";
import { describe, expect, it } from "vitest";
import { mount } from "@vue/test-utils";

import OpenVue from "openvue/config";

import LegendPanel from "@/arches_vue_components/components/MapComponent/components/LegendPanel.vue";

import type {
    MapContext,
    MapLayer,
} from "@/arches_vue_components/components/MapComponent/types.ts";

function buildOverlay(overrides: Partial<MapLayer>): MapLayer {
    return {
        id: 1,
        maplayerid: "overlay",
        name: "Overlay",
        addtomap: true,
        layerdefinitions: [],
        ...overrides,
    };
}

function mountLegendPanel(overlays: MapLayer[]) {
    const context = {
        overlays: ref(overlays),
        overlayOpacities: ref({}),
    } as unknown as MapContext;

    return mount(LegendPanel, {
        props: { context },
        global: { plugins: [OpenVue] },
    });
}

describe("LegendPanel", () => {
    it("shows an empty state when no overlay is visible", () => {
        const wrapper = mountLegendPanel([
            buildOverlay({ maplayerid: "hidden", addtomap: false }),
        ]);

        expect(wrapper.find(".legend-empty").exists()).toBe(true);
        expect(wrapper.findAll(".legend-group")).toHaveLength(0);
    });

    it("groups visible overlays into resource geometries and overlays", () => {
        const wrapper = mountLegendPanel([
            buildOverlay({
                maplayerid: "monuments",
                name: "Monuments",
                is_resource_layer: true,
            }),
            buildOverlay({ maplayerid: "boroughs", name: "Boroughs" }),
            buildOverlay({
                maplayerid: "hidden",
                name: "Hidden",
                addtomap: false,
            }),
        ]);

        const groups = wrapper.findAll(".legend-group");
        expect(groups).toHaveLength(2);
        expect(groups[0].text()).toContain("Resource geometries");
        expect(groups[0].text()).toContain("Monuments");
        expect(groups[1].text()).toContain("Boroughs");
        expect(wrapper.text()).not.toContain("Hidden");
    });

    it("renders a layer's legend markup in place of its swatch", () => {
        const wrapper = mountLegendPanel([
            buildOverlay({ legend: "<strong>Charging area</strong>" }),
        ]);

        expect(wrapper.find(".legend-html strong").text()).toBe(
            "Charging area",
        );
        expect(wrapper.find(".legend-label").exists()).toBe(false);
    });

    it("renders the collapse-all button inline outside a floating panel", async () => {
        const wrapper = mountLegendPanel([buildOverlay({ name: "Boroughs" })]);

        await wrapper.find(".legend-actions button").trigger("click");

        expect(wrapper.find(".legend-row").exists()).toBe(false);
    });

    it("collapses a group's rows", async () => {
        const wrapper = mountLegendPanel([buildOverlay({ name: "Boroughs" })]);

        await wrapper.find(".legend-group-header").trigger("click");

        expect(wrapper.find(".legend-row").exists()).toBe(false);
    });
});
