<script setup lang="ts">
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types";

defineProps<{
    value: NonLocalizedTextValue;
}>();
</script>

<template>
    <div>{{ value?.display_value }}</div>
</template>
