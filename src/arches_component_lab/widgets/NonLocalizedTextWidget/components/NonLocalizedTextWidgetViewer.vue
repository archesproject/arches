<script setup lang="ts">
import type { NonLocalizedTextData } from "@/arches_component_lab/datatypes/non-localized-text/types";

const props = defineProps<{
    value: NonLocalizedTextData | null | undefined;
}>();
</script>

<template>
    <div>{{ props.value?.display_value }}</div>
</template>
