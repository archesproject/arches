<script setup lang="ts">
import { computed } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";

import { searchFrom } from "@/arches_vue_components/components/MapComponent/utils/accessible-geocoder.ts";

import type { GeocoderHosts } from "@/arches_vue_components/components/MapComponent/types.ts";

const CLEAR_EVENT = "clear" as const;

const { hosts, hintId, inputText, isSearching, statusMessage } = defineProps<{
    hosts: GeocoderHosts;
    hintId: string;
    inputText: string;
    isSearching: boolean;
    statusMessage: string;
}>();

const emit = defineEmits<{
    (event: typeof CLEAR_EVENT): void;
}>();

const { $gettext } = useGettext();

const isClearButtonVisible = computed(() => inputText !== "" && !isSearching);
</script>

<template>
    <Teleport :to="hosts.clearHost">
        <Button
            v-if="isClearButtonVisible"
            class="map-geocoder-clear-button"
            icon="pi pi-times"
            variant="text"
            severity="secondary"
            :aria-label="$gettext('Clear search')"
            @click="emit(CLEAR_EVENT)"
        />
    </Teleport>
    <Teleport :to="hosts.searchHost">
        <Button
            class="map-geocoder-search-button"
            variant="text"
            :label="$gettext('Search')"
            @click="searchFrom(hosts.input)"
        />
        <span
            :id="hintId"
            class="map-geocoder-visually-hidden"
        >
            {{
                $gettext(
                    "Type a place name, then press Enter or select Search.",
                )
            }}
        </span>
        <span
            class="map-geocoder-visually-hidden"
            role="status"
            aria-live="polite"
        >
            {{ statusMessage }}
        </span>
    </Teleport>
</template>

<style scoped>
.map-geocoder-clear-button {
    align-self: stretch;
    inline-size: 2.8rem;
    padding: 0;
    color: var(--p-text-muted-color);
}

.map-geocoder-clear-button:not(:disabled):hover {
    background: transparent;
    color: var(--p-text-color);
}

.map-geocoder-clear-button :deep(.p-button-icon) {
    font-size: 1.2rem;
}

.map-geocoder-search-button {
    --p-button-label-font-weight: 600;
    padding-block: 0;
    padding-inline: 1.2rem;
    border: none;
    border-inline-start: 0.1rem solid var(--p-content-border-color);
    border-radius: 0;
    border-start-end-radius: inherit;
    border-end-end-radius: inherit;
    background: var(--p-content-background);
    color: var(--p-primary-color);
    font-size: 1.3rem;
}

.map-geocoder-search-button:not(:disabled):hover {
    border: none;
    border-inline-start: 0.1rem solid var(--p-content-border-color);
    background: var(--p-content-hover-background);
    color: var(--p-primary-color);
}

.map-geocoder-clear-button:focus-visible,
.map-geocoder-search-button:focus-visible {
    outline: 0.2rem solid var(--p-primary-color);
    outline-offset: -0.2rem;
}

.map-geocoder-visually-hidden {
    position: absolute;
    inline-size: 0.1rem;
    block-size: 0.1rem;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
}
</style>
