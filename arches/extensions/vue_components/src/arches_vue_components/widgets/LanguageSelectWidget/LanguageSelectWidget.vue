<script setup lang="ts">
import { computed, ref, watch } from "vue";

import LanguageSelectWidgetEditor from "@/arches_vue_components/widgets/LanguageSelectWidget/components/LanguageSelectWidgetEditor.vue";
import LanguageSelectWidgetViewer from "@/arches_vue_components/widgets/LanguageSelectWidget/components/LanguageSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { useLanguageStore } from "@/arches_vue_components/stores/useLanguageStore.ts";
import { buildLanguageAliasedNodeData } from "@/arches_vue_components/datatypes/language/utils.ts";

import type { LanguageAliasedNodeData } from "@/arches_vue_components/datatypes/language/types.ts";
import type { LanguageSelectWidgetProps } from "@/arches_vue_components/widgets/LanguageSelectWidget/types.ts";

const { aliasedNodeData, value } = defineProps<LanguageSelectWidgetProps>();

const emit = defineEmits<{
    "update:isLoading": [isLoading: boolean];
    "update:value": [updatedValue: string | null];
    "update:aliasedNodeData": [updatedValue: LanguageAliasedNodeData];
    initialized: [updatedValue: LanguageAliasedNodeData];
    ready: [];
}>();

const languageStore = useLanguageStore();
const isLanguagesLoading = ref(true);

languageStore
    .fetchAllLanguages()
    .then(() => {
        isLanguagesLoading.value = false;
    })
    .catch(() => {
        isLanguagesLoading.value = false;
    });

const resolvedAliasedNodeData = computed(() => {
    if (aliasedNodeData) {
        return aliasedNodeData;
    }
    if (isLanguagesLoading.value) {
        return null;
    }
    return buildLanguageAliasedNodeData(value ?? null, languageStore.languages);
});

watch(isLanguagesLoading, (isLoading) => emit("update:isLoading", isLoading));

if (resolvedAliasedNodeData.value) {
    emit("initialized", resolvedAliasedNodeData.value);
    emit("ready");
} else {
    watch(
        resolvedAliasedNodeData,
        (updatedAliasedNodeData) => {
            if (!updatedAliasedNodeData) {
                return;
            }
            emit("initialized", updatedAliasedNodeData);
            emit("ready");
        },
        { once: true },
    );
}

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: LanguageAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value);
}
</script>

<template>
    <LanguageSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        @update:aliased-node-data="onUpdateAliasedNodeData"
    />
    <LanguageSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
    />
</template>
