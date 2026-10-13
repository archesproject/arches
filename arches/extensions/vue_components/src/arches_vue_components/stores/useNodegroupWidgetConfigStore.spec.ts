import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useNodegroupWidgetConfigStore } from "@/arches_vue_components/stores/useNodegroupWidgetConfigStore.ts";

import type { NodegroupWidgetConfig } from "@/arches_vue_components/types.ts";

vi.mock("@/arches_vue_components/application/generate-arches-url.ts", () => ({
    generateArchesURL: (urlName: string) => urlName,
}));

const NAMES_CONFIG: NodegroupWidgetConfig = {
    parent_nodegroup_alias: null,
    cardinality: "n",
    is_writable: true,
    card_x_node_x_widgets: [],
};

describe("useNodegroupWidgetConfigStore", () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        vi.stubGlobal(
            "fetch",
            vi.fn().mockResolvedValue({
                ok: true,
                json: () => Promise.resolve({ names: NAMES_CONFIG }),
            }),
        );
    });

    it("serves nodegroup configs from a graph fetch without another request", async () => {
        const store = useNodegroupWidgetConfigStore();

        await store.fetchGraphWidgetConfigs("person");

        expect(await store.fetchNodegroupWidgetConfigs("person", "names")).toBe(
            NAMES_CONFIG.card_x_node_x_widgets,
        );
        expect(fetch).toHaveBeenCalledOnce();
    });
});
