import { ref } from "vue";
import { describe, expect, it, vi } from "vitest";
import { mount } from "@vue/test-utils";

import OpenVue from "openvue/config";

import OverlayPanel from "@/arches_vue_components/components/MapComponent/components/OverlayPanel/OverlayPanel.vue";

import type {
    MapContext,
    MapLayer,
} from "@/arches_vue_components/components/MapComponent/types.ts";

function buildOverlay(
    maplayerid: string,
    name: string,
    addtomap = true,
): MapLayer {
    return {
        id: 1,
        maplayerid,
        name,
        addtomap,
        layerdefinitions: [
            {
                id: `${maplayerid}-fill`,
                type: "fill",
                paint: { "fill-color": "#ff0000" },
            },
        ],
    };
}

function mountOverlayPanel(overlays: MapLayer[]) {
    const context = {
        overlays: ref(overlays),
        overlayOpacities: ref({}),
        moveOverlay: vi.fn(),
        setOverlayOpacity: vi.fn(),
    } as unknown as MapContext;

    const wrapper = mount(OverlayPanel, {
        props: { context },
        global: { plugins: [OpenVue] },
    });
    return { wrapper, context };
}

describe("OverlayPanel", () => {
    it("toggles an overlay's visibility when its row is clicked", async () => {
        const { wrapper, context } = mountOverlayPanel([
            buildOverlay("boroughs", "Boroughs", false),
        ]);

        await wrapper.find(".overlay-visibility-toggle").trigger("click");

        expect(context.overlays.value[0].addtomap).toBe(true);
    });

    it("moves an overlay down with its reorder button", async () => {
        const { wrapper, context } = mountOverlayPanel([
            buildOverlay("boroughs", "Boroughs"),
            buildOverlay("monuments", "Monuments"),
        ]);

        await wrapper.findAll(".overlay-reorder-button")[1].trigger("click");

        expect(context.moveOverlay).toHaveBeenCalledWith(
            context.overlays.value[0],
            1,
        );
    });

    it("filters overlays and disables reordering while filtering", async () => {
        const { wrapper } = mountOverlayPanel([
            buildOverlay("boroughs", "Boroughs"),
            buildOverlay("monuments", "Monuments"),
        ]);

        await wrapper.find("input").setValue("monu");

        const rows = wrapper.findAll(".overlay-row");
        expect(rows).toHaveLength(1);
        expect(rows[0].text()).toContain("Monuments");
        expect(wrapper.find(".overlay-reorder-hint").exists()).toBe(true);
        expect(
            wrapper
                .findAll(".overlay-reorder-button")
                .every((button) => button.attributes("disabled") !== undefined),
        ).toBe(true);
    });

    it("explains when no overlay matches the filter", async () => {
        const { wrapper } = mountOverlayPanel([
            buildOverlay("boroughs", "Boroughs"),
        ]);

        await wrapper.find("input").setValue("zzz");

        expect(wrapper.find(".overlay-empty").exists()).toBe(true);
    });

    it("shows an opacity control only for visible overlays", () => {
        const { wrapper } = mountOverlayPanel([
            buildOverlay("boroughs", "Boroughs"),
            buildOverlay("monuments", "Monuments", false),
        ]);

        expect(wrapper.findAll(".overlay-opacity-button")).toHaveLength(1);
    });
});
