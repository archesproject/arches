<script setup lang="ts">
import type { URLDatatype } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    value?: URLDatatype | null | undefined;
}>();
</script>
<template>
    <a :href="`${props.value?.url}`">
        {{ props.value?.url_label || props.value?.url }}
    </a>
</template>
