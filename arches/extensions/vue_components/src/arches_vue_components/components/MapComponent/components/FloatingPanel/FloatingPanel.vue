<script setup lang="ts">
import { provide, useId } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";

import { panelHeaderActionsIdKey } from "@/arches_vue_components/components/MapComponent/components/FloatingPanel/injection-keys.ts";

const CLOSE_EVENT = "close" as const;

const {
    title,
    panelId,
    wide = false,
} = defineProps<{
    title: string;
    panelId: string;
    wide?: boolean;
}>();

const emit = defineEmits<{
    (event: typeof CLOSE_EVENT): void;
}>();

const { $gettext } = useGettext();

const headerActionsId = useId();

provide(panelHeaderActionsIdKey, headerActionsId);
</script>

<template>
    <section
        :id="panelId"
        class="floating-panel"
        role="region"
        :class="{ 'floating-panel-wide': wide }"
        :aria-label="title"
    >
        <header class="floating-panel-header">
            <span class="floating-panel-title">{{ title }}</span>
            <div
                :id="headerActionsId"
                class="floating-panel-header-actions"
            />
            <Button
                icon="pi pi-times"
                severity="secondary"
                :text="true"
                :rounded="true"
                :aria-label="$gettext('Close panel')"
                @click="emit(CLOSE_EVENT)"
            />
        </header>
        <div class="floating-panel-body">
            <slot />
        </div>
    </section>
</template>

<style scoped>
.floating-panel {
    display: flex;
    flex-direction: column;
    width: 35rem;
    max-width: 100%;
    max-height: 100%;
    overflow: hidden;
    pointer-events: auto;
    background: var(--p-content-background);
    color: var(--p-text-color);
    border: 0.1rem solid var(--p-content-border-color);
    border-radius: var(--p-content-border-radius);
    box-shadow: 0 0.8rem 2rem var(--p-mask-background);
}

.floating-panel-wide {
    height: 100%;
}

.floating-panel-header {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    gap: 0.8rem;
    padding-block: 0.6rem;
    padding-inline: 1.6rem 0.6rem;
    border-block-end: 0.1rem solid var(--p-content-border-color);
    font-size: 1.45rem;
    font-weight: 700;
}

.floating-panel-title {
    flex: 1;
}

.floating-panel-header-actions {
    display: flex;
    align-items: center;
}

.floating-panel-body {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-height: 0;
    overflow-y: auto;
}
</style>
