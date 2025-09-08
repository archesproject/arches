<script setup lang="ts">
import arches from "arches";

import type { ResourceInstanceValue } from "@/arches_component_lab/datatypes/resource-instance/types";

defineProps<{
    aliasedNodeData: ResourceInstanceValue;
}>();
</script>
<template>
    <div :key="aliasedNodeData?.details?.[0]?.resource_id">
        <a
            :href="`${arches.urls.resource_editor}${aliasedNodeData?.details?.[0]?.resource_id}`"
        >
            {{ aliasedNodeData?.details?.[0]?.display_value }}
        </a>
    </div>
</template>
