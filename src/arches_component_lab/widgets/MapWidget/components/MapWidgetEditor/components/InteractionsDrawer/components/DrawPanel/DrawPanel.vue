<script setup lang="ts">
import { inject, ref } from "vue";
import type { Ref } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import BufferControls from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/components/InteractionsDrawer/components/DrawPanel/components/BufferControls.vue";
import DrawControls from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/components/InteractionsDrawer/components/DrawPanel/components/DrawControls.vue";
import DrawnFeaturesList from "@/arches_component_lab/widgets/MapWidget/components/MapWidgetEditor/components/InteractionsDrawer/components/DrawPanel/components/DrawnFeaturesList.vue";

import type { Feature } from "geojson";
import type { Map as MaplibreMap } from "maplibre-gl";

const { map } = defineProps<{
    map: MaplibreMap;
}>();

const drawnFeatures = inject<Ref<Feature[]>>("drawnFeatures", ref([]));

const { $gettext } = useGettext();

const drawControlsRef = ref<InstanceType<typeof DrawControls> | null>(null);

function deleteSelectedFeature() {
    drawControlsRef.value?.deleteSelectedDrawnFeature();
}

function clearAllDrawnFeatures() {
    drawControlsRef.value?.deleteAllDrawnFeatures();
}
</script>

<template>
    <DrawControls
        ref="drawControlsRef"
        :map="map"
    />
    <BufferControls :map="map" />
    <DrawnFeaturesList
        :map="map"
        :features="drawnFeatures"
    />
    <div class="clear-btns">
        <Button
            size="large"
            severity="secondary"
            @click="deleteSelectedFeature"
        >
            {{ $gettext("Remove Selected") }}
        </Button>
        <Button
            size="large"
            severity="secondary"
            @click="clearAllDrawnFeatures"
        >
            {{ $gettext("Remove All") }}
        </Button>
    </div>
</template>

<style scoped>
.clear-btns {
    display: flex;
    flex-direction: row;
    gap: 1rem;
    padding-block-start: 1rem;
}
</style>
