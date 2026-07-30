<script setup lang="ts">
import { onMounted } from "vue";

import Select from "primevue/select";

import { useLanguageStore } from "@/arches_vue_components/stores/useLanguageStore.ts";
import { buildLanguageAliasedNodeData } from "@/arches_vue_components/datatypes/language/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { LanguageAliasedNodeData } from "@/arches_vue_components/datatypes/language/types.ts";

const { aliasedNodeData, cardXNodeXWidgetData = undefined } = defineProps<{
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData: LanguageAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: LanguageAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: LanguageAliasedNodeData): void;
}>();

const languageStore = useLanguageStore();
languageStore.fetchAllLanguages();

onMounted(() => {
    emit(
        "initialized",
        aliasedNodeData ??
            buildLanguageAliasedNodeData(null, languageStore.languages),
    );
});

function onUpdateModelValue(updatedValue: string | null) {
    emit(
        "update:aliasedNodeData",
        buildLanguageAliasedNodeData(updatedValue, languageStore.languages),
    );
}
</script>

<template>
    <Select
        option-value="code"
        option-label="name"
        :input-id="cardXNodeXWidgetData?.node.alias"
        :options="languageStore.languages"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :fluid="true"
        :model-value="aliasedNodeData?.node_value ?? null"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
