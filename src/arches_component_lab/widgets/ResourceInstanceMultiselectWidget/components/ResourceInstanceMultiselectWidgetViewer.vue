<script setup lang="ts">
import arches from "arches";

import type { ResourceInstanceListValue } from "@/arches_component_lab/datatypes/resource-instance-list/types";

defineProps<{
    value: ResourceInstanceListValue;
}>();
</script>
<template>
    <div
        v-for="resourceInstanceDetail in value?.details"
        :key="resourceInstanceDetail.resource_id"
    >
        <a
            :href="`${arches.urls.resource_editor}${resourceInstanceDetail.resource_id}`"
        >
            {{ resourceInstanceDetail.display_value }}
        </a>
    </div>
</template>
