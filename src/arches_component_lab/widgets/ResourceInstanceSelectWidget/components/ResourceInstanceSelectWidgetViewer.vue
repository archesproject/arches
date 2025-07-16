<script setup lang="ts">
import arches from "arches";

import type { NodeData } from "@/arches_component_lab/types";
import type { ResourceInstanceReference } from "@/arches_component_lab/widgets/types";

const { value } = defineProps<{
    value: NodeData | null | undefined;
}>();
</script>
<template>
    <div
        :key="
            (value?.interchange_value as ResourceInstanceReference).resource_id
        "
    >
        <a
            :href="`${arches.urls.resource_editor}${(value?.interchange_value as ResourceInstanceReference).resource_id}`"
        >
            {{
                (value?.interchange_value as ResourceInstanceReference)
                    .display_value
            }}
        </a>
    </div>
</template>
