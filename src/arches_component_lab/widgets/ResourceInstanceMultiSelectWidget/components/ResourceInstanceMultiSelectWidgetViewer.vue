<script setup lang="ts">
import arches from "arches";
import type { ResourceInstanceReference } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    value?: ResourceInstanceReference[] | undefined;
    configuration: unknown;
}>();
</script>
<template>
    <span>
        <a
            :href="`${arches.urls.resource_editor}${props.value?.[0].resourceId}`"
        >
            {{ props.value?.[0].display_value }}
        </a>
    </span>
</template>
