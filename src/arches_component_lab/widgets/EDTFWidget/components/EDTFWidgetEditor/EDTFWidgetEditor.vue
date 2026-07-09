<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useGettext } from "vue3-gettext";
import InputText from "primevue/inputtext";
import Button from "primevue/button";

import EDTFHelpDrawer from "@/arches_component_lab/widgets/EDTFWidget/components/EDTFWidgetEditor/components/EDTFHelpDrawer.vue";

import { buildEDTFAliasedNodeData } from "@/arches_component_lab/datatypes/edtf/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { EDTFAliasedNodeData } from "@/arches_component_lab/datatypes/edtf/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData: EDTFAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (event: "update:aliasedNodeData", updatedValue: EDTFAliasedNodeData): void;
    (event: "initialized", updatedValue: EDTFAliasedNodeData): void;
}>();

const { $gettext } = useGettext();

const shouldShowHelpDrawer = ref(false);

onMounted(() => {
    emit("initialized", aliasedNodeData ?? buildEDTFAliasedNodeData(null));
});

function handleUpdateModelValue(updatedValue: string | undefined) {
    const newValue = updatedValue ?? "";
    emit("update:aliasedNodeData", buildEDTFAliasedNodeData(newValue || null));
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
            class="p-button-text custom-text-button"
            @click="shouldShowHelpDrawer = true"
        >
            {{ $gettext("EDTF Formatting") }}
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
    width: 100%;
}

.flex-input {
    flex: 1 1 auto;
    min-width: 0;
}

.custom-text-button {
    padding: 0rem 1rem;
}
</style>
