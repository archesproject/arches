<script setup lang="ts">
const props = defineProps<{
    value: string | undefined;
}>();
</script>

<template>
    <span>{{ props.value }}</span>
</template>
