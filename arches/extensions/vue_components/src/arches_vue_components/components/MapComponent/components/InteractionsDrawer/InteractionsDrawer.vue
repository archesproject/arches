<script setup lang="ts">
import Button from "primevue/button";
import Divider from "primevue/divider";

import { useInteractionPanel } from "@/arches_vue_components/components/MapComponent/components/InteractionsDrawer/composables/useInteractionPanel.ts";

import type {
    MapInteractionTool,
    MapContext,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const {
    context,
    items,
    position = "right",
    defaultOpenIndex = undefined,
} = defineProps<{
    context: MapContext;
    items: MapInteractionTool[];
    position?: "left" | "right";
    defaultOpenIndex?: number;
}>();

const {
    selectedItem,
    selectedComponent,
    isOverlayVisible,
    headerContent,
    onItemClick,
} = useInteractionPanel(items, defaultOpenIndex);
</script>

<template>
    <div class="sidebar-container">
        <aside class="sidebar">
            <template
                v-for="item in items"
                :key="item.name"
            >
                <Button
                    class="sidebar-item"
                    text
                    @click="onItemClick(item)"
                >
                    <i :class="item.icon" />
                    <span class="sidebar-item-label">{{ item.name }}</span>
                </Button>
                <Divider :pt="{ root: 'sidebar-item-divider' }" />
            </template>
        </aside>

        <div
            class="sliding-panel"
            :class="[position, { 'is-visible': isOverlayVisible }]"
        >
            <div class="sliding-panel-header">
                <span>{{ headerContent }}</span>
                <Button
                    icon="pi pi-times"
                    severity="secondary"
                    text
                    rounded
                    aria-label="Close"
                    @click="isOverlayVisible = false"
                />
            </div>
            <Divider />

            <component
                :is="selectedComponent"
                :context="context"
                v-bind="selectedItem?.props"
            />
        </div>
    </div>
</template>

<style scoped>
.sidebar-container {
    position: relative;
    display: flex;
    height: 100%;
}

.sidebar {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 7rem;
    border-left: 0.0625rem solid var(--p-menubar-border-color);
    z-index: 1;
}

.sidebar-item {
    flex-direction: column;
    gap: 0.375rem;
    font-size: 1.75rem;
    width: 7rem;
    height: 7rem;
    border-radius: 0;
    color: var(--p-content-color);
}

.sidebar-item-label {
    font-size: 1rem;
}

.sidebar-item-divider {
    margin: 0;
}

.sliding-panel {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 36rem;
    padding: 1rem;
    font-size: 1.125rem;
    background-color: var(--p-content-background);
    box-shadow: 0 0 0.625rem rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
    z-index: 2;
    overflow: auto;
}

.sliding-panel.left {
    left: 7rem;
    transform: translateX(-100%);
}

.sliding-panel.left.is-visible {
    transform: translateX(0);
}

.sliding-panel.right {
    right: 0;
    transform: translateX(100%);
}

.sliding-panel.right.is-visible {
    transform: translateX(0);
}

.sliding-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    font-size: 1.25rem;
    font-weight: bold;
}
</style>
