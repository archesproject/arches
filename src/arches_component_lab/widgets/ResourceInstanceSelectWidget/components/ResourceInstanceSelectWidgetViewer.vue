<script setup lang="ts">
import { watch } from "vue";

import arches from "arches";

import type { ResourceInstanceAliasedNodeData } from "@/arches_component_lab/datatypes/resource-instance/types";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData?: ResourceInstanceAliasedNodeData | null;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: ResourceInstanceAliasedNodeData];
}>();

watch(
    () => aliasedNodeData,
    (newValue) => {
        if (newValue) {
            emit("initialized", newValue);
        }
    },
    { immediate: true },
);
</script>

<template>
    <div :key="aliasedNodeData?.node_value?.[0]?.resourceId ?? undefined">
        <a
            :href="`${arches.urls.resource_editor}${aliasedNodeData?.node_value?.[0]?.resourceId}`"
            class="resource-instance-link"
        >
            {{ aliasedNodeData?.display_value }}
        </a>
    </div>
</template>
