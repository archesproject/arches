<script setup lang="ts">
import arches from "arches";
import type { ResourceInstanceReference } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    value?: ResourceInstanceReference | null | undefined;
}>();
</script>
<template>
    <div :key="props.value?.resource_id">
        <a :href="`${arches.urls.resource_editor}${props.value?.resource_id}`">
            {{ props.value?.display_value }}
        </a>
    </div>
</template>
