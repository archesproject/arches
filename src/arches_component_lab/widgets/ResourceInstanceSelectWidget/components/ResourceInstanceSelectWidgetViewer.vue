<script setup lang="ts">
import arches from "arches";
import type { ResourceInstanceReference } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    initialValue?: ResourceInstanceReference[];
    configuration: any;
}>();
</script>
<template>
    <span>
        <a :href="`${arches.urls.resource_editor}${props.initialValue?.[0].resourceId}`">
            {{ props.initialValue?.[0].display_value }}
        </a>
    </span>
</template>
