<script setup lang="ts">
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types";

const props = defineProps<{
    value: NonLocalizedTextValue | null | undefined;
}>();
</script>

<template>
    <div>{{ props.value?.display_value }}</div>
</template>
