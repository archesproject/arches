<script setup lang="ts">
import { ref } from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import InputText from "openvue/inputtext";

import EDTFHelpDrawer from "@/arches_vue_components/widgets/EDTFWidget/components/EDTFWidgetEditor/components/EDTFHelpDrawer.vue";

import { buildEDTFAliasedNodeData } from "@/arches_vue_components/datatypes/edtf/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { EDTFAliasedNodeData } from "@/arches_vue_components/datatypes/edtf/types.ts";

const UPDATE_ALIASED_NODE_DATA_EVENT = "update:aliasedNodeData" as const;

const { cardXNodeXWidgetData = undefined, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData: EDTFAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (
        event: typeof UPDATE_ALIASED_NODE_DATA_EVENT,
        updatedValue: EDTFAliasedNodeData,
    ): void;
}>();

const { $gettext } = useGettext();

const shouldShowHelpDrawer = ref(false);

function handleUpdateModelValue(updatedValue: string | undefined): void {
    const newValue = updatedValue ?? "";
    emit(
        UPDATE_ALIASED_NODE_DATA_EVENT,
        buildEDTFAliasedNodeData(newValue || null),
    );
}
</script>

<template>
    <div class="field-with-button">
        <InputText
            class="flex-input"
            type="text"
            :fluid="true"
            :model-value="aliasedNodeData?.node_value ?? ''"
            :placeholder="cardXNodeXWidgetData?.config.placeholder"
            :pt="{ root: { id: cardXNodeXWidgetData?.node.alias } }"
            @update:model-value="handleUpdateModelValue"
        />
        <Button
            class="custom-text-button"
            variant="text"
            size="small"
            @click="shouldShowHelpDrawer = true"
        >
            <span>{{ $gettext("EDTF Formatting") }}</span>
        </Button>

        <EDTFHelpDrawer
            v-model:should-show-help-drawer="shouldShowHelpDrawer"
        />
    </div>
</template>

<style scoped>
.field-with-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    inline-size: 100%;
}

.flex-input {
    flex: 1 1 auto;
    min-inline-size: 0;
}

.custom-text-button {
    padding-block: 0.75rem;
    padding-inline: 1rem;
    font-size: 1.1rem;
}
</style>
