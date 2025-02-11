<script setup lang="ts">
import arches from "arches";

const props = defineProps<{
    initialValue: string | undefined;
    configuration: any;
}>();
</script>
<template>
    <span>
        <a :href="`${arches.urls.resource_editor}${val.resourceId}`">
            {{ val.display_value }}
        </a>
    </span>
</template>
