<script setup lang="ts">
import { watch } from "vue";

import arches from "arches";

import type { ResourceInstanceListAliasedNodeData } from "@/arches_vue_components/datatypes/resource-instance-list/types";

const { aliasedNodeData = null } = defineProps<{
    aliasedNodeData?: ResourceInstanceListAliasedNodeData | null;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: ResourceInstanceListAliasedNodeData];
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
    <div
        v-for="item in aliasedNodeData?.details"
        :key="item.resource_id"
    >
        <a
            :href="`${arches.urls.resource_editor}${item.resource_id}`"
            class="resource-instance-link"
        >
            {{ item.display_value }}
        </a>
    </div>
</template>
