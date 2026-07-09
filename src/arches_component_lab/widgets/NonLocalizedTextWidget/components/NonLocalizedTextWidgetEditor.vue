<script setup lang="ts">
import { onMounted } from "vue";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";

import { MULTILINE_RENDER_CONTEXT } from "@/arches_component_lab/widgets/NonLocalizedTextWidget/constants.ts";

import { buildNonLocalizedTextAliasedNodeData } from "@/arches_component_lab/datatypes/non-localized-text/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { NonLocalizedTextAliasedNodeData } from "@/arches_component_lab/datatypes/non-localized-text/types.ts";

const { cardXNodeXWidgetData, renderContext, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    renderContext?: string;
    aliasedNodeData: NonLocalizedTextAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: NonLocalizedTextAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: NonLocalizedTextAliasedNodeData): void;
}>();

onMounted(() => {
    emit(
        "initialized",
        aliasedNodeData ?? buildNonLocalizedTextAliasedNodeData(null),
    );
});

function onUpdateModelValue(updatedValue: string | undefined) {
    const newValue = updatedValue ?? null;
    emit(
        "update:aliasedNodeData",
        buildNonLocalizedTextAliasedNodeData(newValue),
    );
}
</script>

<template>
    <Textarea
        v-if="renderContext === MULTILINE_RENDER_CONTEXT"
        :auto-resize="true"
        :fluid="true"
        :model-value="aliasedNodeData?.node_value ?? ''"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :pt="{ root: { id: cardXNodeXWidgetData?.node.alias } }"
        rows="4"
        @update:model-value="onUpdateModelValue($event)"
    />
    <InputText
        v-else
        type="text"
        :fluid="true"
        :model-value="aliasedNodeData?.node_value ?? ''"
        :placeholder="cardXNodeXWidgetData?.config.placeholder"
        :pt="{ root: { id: cardXNodeXWidgetData?.node.alias } }"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
