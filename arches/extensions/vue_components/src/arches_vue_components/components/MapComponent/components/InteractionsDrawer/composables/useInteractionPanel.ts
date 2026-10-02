import { computed, onMounted, ref, shallowRef } from "vue";

import type { Component, ComputedRef, Ref, ShallowRef } from "vue";
import type { MapInteractionTool } from "@/arches_vue_components/components/MapComponent/types.ts";

export interface UseInteractionPanelReturn {
    selectedItem: ShallowRef<MapInteractionTool | null>;
    selectedComponent: ComputedRef<Component | null>;
    isOverlayVisible: Ref<boolean>;
    headerContent: ComputedRef<string | null>;
    openPanel: (item: MapInteractionTool) => void;
    closePanel: () => void;
    onItemClick: (item: MapInteractionTool) => void;
}

export function useInteractionPanel(
    items: MapInteractionTool[],
    defaultOpenIndex?: number,
): UseInteractionPanelReturn {
    const selectedItem = shallowRef<MapInteractionTool | null>(null);
    const isOverlayVisible = ref(false);

    const selectedComponent = computed(
        () => selectedItem.value?.component ?? null,
    );
    const headerContent = computed(() => selectedItem.value?.header ?? null);

    function openPanel(item: MapInteractionTool): void {
        selectedItem.value = item;
        isOverlayVisible.value = true;
    }

    function closePanel(): void {
        isOverlayVisible.value = false;
    }

    function onItemClick(item: MapInteractionTool): void {
        if (selectedItem.value === item) {
            isOverlayVisible.value = !isOverlayVisible.value;
        } else {
            openPanel(item);
        }
    }

    onMounted(() => {
        if (defaultOpenIndex !== undefined) {
            const item = items[defaultOpenIndex];

            if (item) {
                openPanel(item);
            }
        }
    });

    return {
        selectedItem,
        selectedComponent,
        isOverlayVisible,
        headerContent,
        openPanel,
        closePanel,
        onItemClick,
    };
}
