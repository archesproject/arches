<script setup lang="ts">
import arches from "arches";
import type { ResourceInstanceReference } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    value?: ResourceInstanceReference | null | undefined;
}>();
</script>
<template>
    <div :key="props.value?.resourceId">
        <a :href="`${arches.urls.resource_editor}${props.value?.resourceId}`">
            {{ props.value?.display_value }}
        </a>
    </div>
</template>
