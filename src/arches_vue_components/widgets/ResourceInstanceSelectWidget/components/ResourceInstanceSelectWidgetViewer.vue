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
            :href="
                generateArchesURL('arches:resource_editor', {
                    resourceid:
                        aliasedNodeData?.node_value?.[0]?.resourceId ?? '',
                })
            "
            class="resource-instance-link"
        >
            {{ aliasedNodeData?.display_value }}
        </a>
    </div>
</template>
