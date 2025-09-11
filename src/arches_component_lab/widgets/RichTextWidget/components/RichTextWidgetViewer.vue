<script setup lang="ts">
import { computed } from "vue";
import DOMPurify from "dompurify";
import type { StringValue } from "@/arches_component_lab/datatypes/string/types";

const { aliasedNodeData } = defineProps<{ aliasedNodeData?: StringValue }>();

const cleanHtml = computed(() =>
    DOMPurify.sanitize(aliasedNodeData?.display_value ?? "", {
        USE_PROFILES: { html: true },
    }),
);
</script>

<template>
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div v-html="cleanHtml"></div>
</template>
