import { useGettext } from "vue3-gettext";

import BasemapPanel from "@/arches_vue_components/components/MapComponent/components/BasemapPanel/BasemapPanel.vue";
import LegendPanel from "@/arches_vue_components/components/MapComponent/components/LegendPanel.vue";
import MapToolsPanel from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/MapToolsPanel.vue";
import OverlayPanel from "@/arches_vue_components/components/MapComponent/components/OverlayPanel/OverlayPanel.vue";
import SettingsPanel from "@/arches_vue_components/components/MapComponent/components/SettingsPanel/SettingsPanel.vue";

import {
    BASEMAP_TOOL_ID,
    LEGEND_TOOL_ID,
    MAP_TOOLS_TOOL_ID,
    OVERLAYS_TOOL_ID,
    SETTINGS_TOOL_ID,
} from "@/arches_vue_components/components/MapComponent/constants.ts";

import type {
    MapContext,
    MapInteractionTool,
} from "@/arches_vue_components/components/MapComponent/types.ts";

function countVisibleOverlays(context: MapContext): number {
    return context.overlays.value.filter((overlay) => overlay.addtomap).length;
}

export function useDefaultMapInteractionTools(): MapInteractionTool[] {
    const { $gettext } = useGettext();

    return [
        {
            id: MAP_TOOLS_TOOL_ID,
            name: $gettext("Map Tools"),
            header: $gettext("Map Tools"),
            component: MapToolsPanel,
            icon: "pi pi-pencil",
            wide: true,
        },
        {
            id: BASEMAP_TOOL_ID,
            name: $gettext("Basemap"),
            header: $gettext("Basemap"),
            component: BasemapPanel,
            icon: "pi pi-globe",
        },
        {
            id: OVERLAYS_TOOL_ID,
            name: $gettext("Overlays"),
            header: $gettext("Overlays"),
            component: OverlayPanel,
            icon: "pi pi-list",
            badgeCount: countVisibleOverlays,
        },
        {
            id: LEGEND_TOOL_ID,
            name: $gettext("Legend"),
            header: $gettext("Legend"),
            component: LegendPanel,
            icon: "pi pi-book",
        },
        {
            id: SETTINGS_TOOL_ID,
            name: $gettext("Settings"),
            header: $gettext("Settings"),
            component: SettingsPanel,
            icon: "pi pi-cog",
        },
    ];
}
