<script setup lang="ts">
const props = defineProps<{
    value: string | null | undefined;
}>();
</script>

<template>
    <div>{{ props.value }}</div>
</template>
