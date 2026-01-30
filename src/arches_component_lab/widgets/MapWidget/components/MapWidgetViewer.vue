<script setup lang="ts">
import type { GeoJSONFeatureCollectionValue } from "@/arches_component_lab/datatypes/geojson-feature-collection/types";

defineProps<{
    aliasedNodeData: GeoJSONFeatureCollectionValue | null;
}>();
</script>

<template>
    <div>{{ aliasedNodeData?.display_value }}</div>
</template>
