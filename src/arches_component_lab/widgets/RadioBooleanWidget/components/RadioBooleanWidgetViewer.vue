<script setup lang="ts">
const props = defineProps<{
    value: string | null | undefined;
}>();
</script>

<template>
    <div>{{ props.value.display_value }}</div>
</template>
