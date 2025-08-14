<script setup lang="ts">
import type { StringValue } from "@/arches_component_lab/datatypes/string/types";

defineProps<{ value?: StringValue }>();
</script>

<template>
    <div>{{ value?.display_value }}</div>
</template>
