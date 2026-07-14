<script setup lang="ts">
import { computed, ref, watch, watchEffect } from "vue";

import { useGettext } from "vue3-gettext";

import ReferenceSelectWidgetEditor from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetEditor.vue";
import ReferenceSelectWidgetViewer from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_vue_components/widgets/constants.ts";
import { useLanguageStore } from "@/arches_vue_components/stores/useLanguageStore.ts";
import { buildReferenceSelectAliasedNodeData } from "@/arches_controlled_lists/datatypes/reference-select/utils.ts";

import type { WidgetMode } from "@/arches_vue_components/widgets/types";
import type { Language } from "@/arches_vue_components/types";
import type {
    ReferenceSelectAliasedNodeData,
    ReferenceSelectDatatypeCardXNodeXWidgetData,
    ReferenceSelectNodeValue,
} from "@/arches_controlled_lists/datatypes/reference-select/types";

const { aliasedNodeData, value } = defineProps([
    "mode",
    "nodeAlias",
    "graphSlug",
    "cardXNodeXWidgetData",
    "aliasedNodeData",
    "value",
]) as {
    mode: WidgetMode;
    nodeAlias?: string;
    graphSlug?: string;
    cardXNodeXWidgetData?: ReferenceSelectDatatypeCardXNodeXWidgetData;
    aliasedNodeData?: ReferenceSelectAliasedNodeData | null;
    value?: ReferenceSelectNodeValue[] | null;
};

const emit = defineEmits([
    "update:isLoading",
    "update:value",
    "update:aliasedNodeData",
    "initialized",
]) as {
    (event: "update:isLoading", isLoading: boolean): void;
    (event: "update:value", updatedValue: ReferenceSelectNodeValue[]): void;
    (
        event: "update:aliasedNodeData",
        updatedValue: ReferenceSelectAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: ReferenceSelectAliasedNodeData): void;
};

const { current: preferredLanguageCode } = useGettext();
const languageStore = useLanguageStore();

const systemLanguageCode = computed(
    () =>
        languageStore.languages.find((lang: Language) => lang.isdefault)
            ?.code ?? preferredLanguageCode,
);

const isEditorLoading = ref(false);

const resolvedAliasedNodeData = computed(() => {
    if (aliasedNodeData) {
        return aliasedNodeData;
    }
    return buildReferenceSelectAliasedNodeData(
        value ?? null,
        preferredLanguageCode,
        systemLanguageCode.value,
    );
});

watchEffect(() => {
    languageStore.fetchAllLanguages();
});

watch(isEditorLoading, (isLoading) => emit("update:isLoading", isLoading));

function onUpdateAliasedNodeData(
    updatedAliasedNodeData: ReferenceSelectAliasedNodeData,
) {
    emit("update:aliasedNodeData", updatedAliasedNodeData);
    emit("update:value", updatedAliasedNodeData.node_value ?? []);
}
</script>

<template>
    <ReferenceSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="resolvedAliasedNodeData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :system-language-code="systemLanguageCode"
        @update:is-loading="isEditorLoading = $event"
        @update:aliased-node-data="onUpdateAliasedNodeData"
        @initialized="emit('initialized', $event)"
    />
    <ReferenceSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="resolvedAliasedNodeData"
        :system-language-code="systemLanguageCode"
        @initialized="emit('initialized', $event)"
    />
</template>
