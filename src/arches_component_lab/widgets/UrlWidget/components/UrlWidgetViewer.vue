<script setup lang="ts">
import type { Url } from "@/arches_lingo/types.ts";

const props = defineProps<{
    value?: Url | null | undefined;
}>();
</script>
<template>
    <a :href="`${props.value?.url}`">
        {{ props.value?.url_label || props.value?.url }}
    </a>
</template>
