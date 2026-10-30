<script setup lang="ts">
import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

import type { ResourceInstanceListAliasedNodeData } from "@/arches_vue_components/datatypes/resource-instance-list/types";

defineProps<{
    aliasedNodeData?: ResourceInstanceListAliasedNodeData | null;
}>();
</script>

<template>
    <div
        v-for="item in aliasedNodeData?.details"
        :key="item.resource_id"
    >
        <a
            :href="
                generateArchesURL('arches:resource_editor', {
                    resourceid: item.resource_id,
                })
            "
            class="resource-instance-link"
        >
            {{ item.display_value }}
        </a>
    </div>
</template>

<style scoped>
.resource-instance-link {
    color: var(--p-primary-color);
}

.resource-instance-link:hover {
    color: var(--p-primary-hover-color);
}
</style>
