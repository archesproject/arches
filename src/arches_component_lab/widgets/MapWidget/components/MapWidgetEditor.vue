<script setup lang="ts">
import InputText from "primevue/inputtext";

import type { GeoJSONFeatureCollectionValue } from "@/arches_component_lab/datatypes/geojson-feature-collection/types";

defineProps<{
    aliasedNodeData: GeoJSONFeatureCollectionValue | null;
}>();
</script>

<template>
    <InputText
        disabled
        type="text"
        :fluid="true"
        :model-value="aliasedNodeData?.display_value || ''"
    />
</template>
