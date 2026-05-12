<script setup lang="ts">
import { inject, onMounted, ref, watch } from "vue";

import RadioButton from "primevue/radiobutton";

import type { Map } from "maplibre-gl";
import type { PropType, Ref } from "vue";

import type { Basemap } from "@/arches_component_lab/widgets/MapWidget/types.ts";

defineProps({
    map: {
        type: Object as PropType<Map>,
        required: true,
    },
});

const basemaps = inject<Ref<Basemap[]>>("basemaps", ref([]));
const selectedBasemap = ref<Basemap | null>(null);

watch(selectedBasemap, (newBasemap) => {
    basemaps.value.forEach((basemap) => {
        basemap.active = basemap === newBasemap;
    });
});

onMounted(() => {
    const activeBasemap = basemaps.value.find((basemap) => basemap.active);
    if (activeBasemap) {
        selectedBasemap.value = activeBasemap;
    }
});
</script>

<template>
    <div
        v-for="basemap in basemaps"
        :key="basemap.id"
    >
        <div
            class="basemap-item"
            @click="selectedBasemap = basemap"
        >
            <RadioButton
                v-model="selectedBasemap"
                :value="basemap"
                :label="basemap.name"
                @click.stop
            />
            <label>{{ basemap.name }}</label>
        </div>
    </div>
</template>

<style scoped>
.basemap-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem;
    border-block-end: 0.0625rem solid var(--p-content-border-color);
    cursor: pointer;
}

.basemap-item label {
    line-height: 1;
    margin-block-end: 0;
    cursor: pointer;
}

.basemap-item:hover {
    background: var(--p-button-secondary-hover-background);
}
</style>
