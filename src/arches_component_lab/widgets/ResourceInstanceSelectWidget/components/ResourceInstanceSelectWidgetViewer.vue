<script setup lang="ts">
import arches from "arches";

import type { ResourceInstanceValue } from "@/arches_component_lab/datatypes/resource-instance/types";

defineProps<{
    value: ResourceInstanceValue;
}>();
</script>
<template>
    <div :key="value?.details[0].resource_id">
        <a
            :href="`${arches.urls.resource_editor}${value?.details[0].resource_id}`"
        >
            {{ value?.details[0].display_value }}
        </a>
    </div>
</template>
