<script setup lang="ts">
const props = defineProps<{
    value: string | undefined;
}>();
</script>

<template>
    <div>{{ props.value }}</div>
</template>
