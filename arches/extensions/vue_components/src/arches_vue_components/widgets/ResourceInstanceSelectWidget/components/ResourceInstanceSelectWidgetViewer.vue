<script setup lang="ts">
import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

import type { ResourceInstanceAliasedNodeData } from "@/arches_vue_components/datatypes/resource-instance/types";

defineProps<{
    aliasedNodeData?: ResourceInstanceAliasedNodeData | null;
}>();
</script>

<template>
    <div :key="aliasedNodeData?.node_value?.[0]?.resourceId ?? undefined">
        <a
            v-if="aliasedNodeData?.display_value"
            class="resource-instance-link"
            :href="
                generateArchesURL('arches:resource_editor', {
                    resourceid:
                        aliasedNodeData?.node_value?.[0]?.resourceId ?? '',
                })
            "
        >
            {{ aliasedNodeData?.display_value }}
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
