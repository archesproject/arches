<script setup lang="ts">
import type { NonLocalizedTextValue } from "@/arches_component_lab/datatypes/non-localized-text/types";

defineProps<{
    value: NonLocalizedTextValue | null | undefined;
}>();
</script>

<template>
    <div>{{ value?.display_value }}</div>
</template>
