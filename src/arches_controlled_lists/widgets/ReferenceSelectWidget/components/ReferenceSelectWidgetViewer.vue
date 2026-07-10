<script setup lang="ts">
import { computed, onMounted } from "vue";

import { useGettext } from "vue3-gettext";

import { buildReferenceSelectAliasedNodeData } from "@/arches_controlled_lists/datatypes/reference-select/utils.ts";

import type { ReferenceSelectAliasedNodeData } from "@/arches_controlled_lists/datatypes/reference-select/types";

const { aliasedNodeData, systemLanguageCode } = defineProps<{
    aliasedNodeData?: ReferenceSelectAliasedNodeData | null;
    systemLanguageCode: string;
}>();

const emit = defineEmits<{
    initialized: [updatedValue: ReferenceSelectAliasedNodeData];
}>();

const { current: preferredLanguageCode } = useGettext();

const displayValue = computed(() => aliasedNodeData?.display_value);

onMounted(() => {
    emit(
        "initialized",
        aliasedNodeData ??
            buildReferenceSelectAliasedNodeData(
                null,
                preferredLanguageCode,
                systemLanguageCode,
            ),
    );
});
</script>

<template>
    <span>{{ displayValue }}</span>
</template>
