<script setup lang="ts">
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";

import BufferControls from "@/arches_vue_components/components/MapComponent/components/InteractionsDrawer/components/DrawPanel/components/BufferControls.vue";
import DrawControls from "@/arches_vue_components/components/MapComponent/components/InteractionsDrawer/components/DrawPanel/components/DrawControls.vue";
import DrawnFeaturesList from "@/arches_vue_components/components/MapComponent/components/InteractionsDrawer/components/DrawPanel/components/DrawnFeaturesList.vue";
import ShapefileDropZone from "@/arches_vue_components/components/MapComponent/components/InteractionsDrawer/components/DrawPanel/components/ShapefileDropZone.vue";

import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const resolvedContext = useResolvedMapContext(context, "DrawPanel");
const { deleteSelectedDrawnFeature, deleteAllDrawnFeatures } = resolvedContext;

const { $gettext } = useGettext();
</script>

<template>
    <div class="draw-panel">
        <ShapefileDropZone :context="resolvedContext" />
        <DrawControls :context="resolvedContext" />
        <BufferControls :context="resolvedContext" />
        <DrawnFeaturesList :context="resolvedContext" />
        <div class="clear-btns">
            <Button
                size="large"
                severity="secondary"
                @click="deleteSelectedDrawnFeature"
            >
                {{ $gettext("Remove Selected") }}
            </Button>
            <Button
                size="large"
                severity="secondary"
                @click="deleteAllDrawnFeatures"
            >
                {{ $gettext("Remove All") }}
            </Button>
        </div>
    </div>
</template>

<style scoped>
.draw-panel {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.clear-btns {
    display: flex;
    flex-direction: row;
    gap: 1rem;
}
</style>
