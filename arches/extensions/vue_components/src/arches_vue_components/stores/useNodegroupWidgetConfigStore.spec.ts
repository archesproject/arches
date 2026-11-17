import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useNodegroupWidgetConfigStore } from "@/arches_vue_components/stores/useNodegroupWidgetConfigStore.ts";
import { useWidgetConfigStore } from "@/arches_vue_components/stores/useWidgetConfigStore.ts";

import type {
    CardXNodeXWidgetData,
    NodegroupWidgetConfig,
} from "@/arches_vue_components/types.ts";

const GRAPH_SLUG = "names-graph";
const GRAPH_WIDGET_CONFIGS_URL =
    "arches_vue_components:api-card-x-node-x-widget-list-from-graph";
const NODE_WIDGET_CONFIG_URL = "arches_vue_components:api-card-x-node-x-widget";

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

const NODE_WIDGET: CardXNodeXWidgetData = {
    ...WIDGET,
    id: "name-content-node-widget",
};

const GRAPH_WIDGET_CONFIGS: Record<string, NodegroupWidgetConfig> = {
    names: {
        parent_nodegroup_alias: null,
        cardinality: "n",
        is_writable: true,
        card: WIDGET.card,
        card_x_node_x_widgets: [WIDGET],
    },
};

vi.mock("@/arches_vue_components/application/generate-arches-url.ts", () => ({
    generateArchesURL: (urlName: string) => urlName,
}));

describe("useNodegroupWidgetConfigStore", () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        vi.stubGlobal(
            "fetch",
            vi.fn((url: string) => {
                if (url === GRAPH_WIDGET_CONFIGS_URL) {
                    return Promise.resolve(
                        new Response(JSON.stringify(GRAPH_WIDGET_CONFIGS)),
                    );
                }
                return Promise.resolve(
                    new Response(JSON.stringify(NODE_WIDGET)),
                );
            }),
        );
    });

    it("serves per-node widget configs from the graph configs", async () => {
        await useNodegroupWidgetConfigStore().fetchGraphWidgetConfigs(
            GRAPH_SLUG,
        );

        const cardXNodeXWidget = await useWidgetConfigStore().fetchWidgetConfig(
            GRAPH_SLUG,
            WIDGET.node.alias,
        );

        expect(cardXNodeXWidget).toEqual(WIDGET);
        expect(fetch).toHaveBeenCalledTimes(1);
        expect(fetch).toHaveBeenCalledWith(GRAPH_WIDGET_CONFIGS_URL);
    });

    it("keeps a per-node widget config that was already requested", async () => {
        const widgetConfigStore = useWidgetConfigStore();
        await widgetConfigStore.fetchWidgetConfig(
            GRAPH_SLUG,
            WIDGET.node.alias,
        );

        await useNodegroupWidgetConfigStore().fetchGraphWidgetConfigs(
            GRAPH_SLUG,
        );

        const cardXNodeXWidget = await widgetConfigStore.fetchWidgetConfig(
            GRAPH_SLUG,
            WIDGET.node.alias,
        );

        expect(cardXNodeXWidget).toEqual(NODE_WIDGET);
        expect(fetch).toHaveBeenCalledWith(NODE_WIDGET_CONFIG_URL);
    });
});
