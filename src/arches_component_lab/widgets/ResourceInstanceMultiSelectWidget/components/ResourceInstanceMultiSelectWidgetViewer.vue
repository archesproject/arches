<script setup lang="ts">
import arches from "arches";
import type { ResourceInstanceReference } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    value?: ResourceInstanceReference[] | null | undefined;
}>();
</script>
<template>
    <div
        v-for="resourceInstance in props.value"
        :key="resourceInstance.resource_id"
    >
        <a
            :href="`${arches.urls.resource_editor}${resourceInstance.interchange_value}`"
        >
            {{ resourceInstance.display_value }}
        </a>
    </div>
</template>
