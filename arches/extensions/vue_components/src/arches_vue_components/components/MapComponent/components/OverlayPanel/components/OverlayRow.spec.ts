import { ref } from "vue";
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";
import { createGettext } from "vue3-gettext";

import Checkbox from "openvue/checkbox";
import OpenVue from "openvue/config";

import OverlayRow from "@/arches_vue_components/components/MapComponent/components/OverlayPanel/components/OverlayRow.vue";

import type { MapLayer } from "@/arches_vue_components/components/MapComponent/types.ts";

vi.mock(
    "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts",
    () => ({
        useResolvedMapContext: () => ({
            overlays: ref([]),
            overlayOpacities: ref({}),
            moveOverlay: vi.fn(),
            setOverlayOpacity: vi.fn(),
        }),
    }),
);

describe("OverlayRow visibility", () => {
    it.each([true, false])(
        "reflects visibility %s and emits a toggle without mutating the overlay",
        async (addtomap) => {
            const overlay: MapLayer = {
                id: 1,
                maplayerid: "test-overlay",
                name: "Test overlay",
                addtomap,
                layerdefinitions: [],
            };
            const wrapper = mount(OverlayRow, {
                global: {
                    plugins: [OpenVue, createGettext({ silent: true })],
                },
                props: {
                    overlay,
                    isReorderDisabled: false,
                    isDragTarget: false,
                },
            });
            const checkbox = wrapper.getComponent(Checkbox);
            const input = checkbox.get<HTMLInputElement>(
                'input[type="checkbox"]',
            );

            expect(input.element.checked).toBe(addtomap);
            expect(
                wrapper.get(".overlay-reorder-buttons").element
                    .nextElementSibling,
            ).toBe(checkbox.element);
            expect(wrapper.get("label").attributes("for")).toBe(
                input.attributes("id"),
            );
            expect(wrapper.get("label").text()).toBe(overlay.name);
            expect(wrapper.find(".overlay-visibility-toggle").exists()).toBe(
                false,
            );

            await input.setValue(!addtomap);

            expect(wrapper.emitted("toggle-visibility")).toEqual([[]]);
            expect(overlay.addtomap).toBe(addtomap);

            await wrapper.setProps({
                overlay: { ...overlay, addtomap: !addtomap },
            });

            expect(input.element.checked).toBe(!addtomap);
            wrapper.unmount();
        },
    );
});
