<script setup lang="ts">
import arches from "arches";

import type { ResourceInstanceReference } from "@/arches_component_lab/widgets/types.ts";
import type { NodeData } from "@/arches_component_lab/types.ts";

const { value } = defineProps<{
    value: NodeData | null | undefined;
}>();
</script>
<template>
    <div
        v-for="resourceInstance in value?.interchange_value as ResourceInstanceReference[]"
        :key="resourceInstance.resource_id"
    >
        <a
            :href="`${arches.urls.resource_editor}${resourceInstance.interchange_value}`"
        >
            {{ resourceInstance.display_value }}
        </a>
    </div>
</template>
