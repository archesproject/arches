<script setup lang="ts">
import { computed, useTemplateRef } from "vue";

import { useGettext } from "vue3-gettext";

import Badge from "openvue/badge";
import Button from "openvue/button";

import type {
    MapContext,
    MapInteractionTool,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const TOGGLE_TOOL_EVENT = "toggle-tool" as const;

const { tools, activeToolName, panelId, context } = defineProps<{
    tools: MapInteractionTool[];
    activeToolName: string | null;
    panelId: string;
    context: MapContext;
}>();

const emit = defineEmits<{
    (event: typeof TOGGLE_TOOL_EVENT, toolName: string): void;
}>();

const headerElement = useTemplateRef<HTMLDivElement>("headerElement");

defineExpose({ focusTool });

const { $gettext } = useGettext();

const badgeCountsByToolName = computed(() =>
    Object.fromEntries(
        tools.map((tool) => [tool.name, tool.badgeCount?.(context) ?? 0]),
    ),
);

function focusTool(toolName: string): void {
    headerElement.value
        ?.querySelector<HTMLButtonElement>(`[data-tool-name="${toolName}"]`)
        ?.focus();
}
</script>

<template>
    <div
        ref="headerElement"
        class="map-header"
        role="toolbar"
        :aria-label="$gettext('Map tools')"
    >
        <Button
            v-for="tool in tools"
            :key="tool.name"
            class="map-header-button"
            :class="{
                'map-header-button-active': tool.name === activeToolName,
            }"
            :data-tool-name="tool.name"
            :aria-expanded="tool.name === activeToolName"
            :aria-controls="panelId"
            :text="true"
            @click="emit(TOGGLE_TOOL_EVENT, tool.name)"
        >
            <i
                aria-hidden="true"
                :class="tool.icon"
            />
            <span>{{ tool.name }}</span>
            <Badge
                v-if="badgeCountsByToolName[tool.name]"
                :value="badgeCountsByToolName[tool.name]"
            />
        </Button>
    </div>
</template>

<style scoped>
.map-header {
    display: flex;
    flex: 0 0 auto;
    border-block-end: 0.1rem solid var(--p-content-border-color);
    background: var(--p-content-background);
}

.map-header-button {
    gap: 0.8rem;
    min-height: 4.4rem;
    padding-block: 1.1rem;
    padding-inline: 1.75rem;
    border-radius: 0;
    color: var(--p-text-muted-color);
    font-size: 1.35rem;
    font-weight: 600;
}

.map-header-button.map-header-button-active {
    color: var(--p-primary-color);
    background: var(--p-highlight-background);
    box-shadow: inset 0 -0.2rem 0 var(--p-primary-color);
}
</style>
