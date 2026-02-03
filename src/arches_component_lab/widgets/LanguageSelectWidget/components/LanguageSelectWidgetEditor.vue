<script setup lang="ts">
import { ref, watchEffect } from "vue";

import Select from "primevue/select";

import { fetchLanguages } from "@/arches_component_lab/widgets/api.ts";

import type { Ref } from "vue";
import type {
    CardXNodeXWidgetData,
    Language,
} from "@/arches_component_lab/types.ts";
import type { LanguageValue } from "@/arches_component_lab/datatypes/language/types.ts";

const {
    aliasedNodeData,
    cardXNodeXWidgetData,
    shouldEmitSimplifiedValue = false,
} = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    aliasedNodeData: LanguageValue | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: LanguageValue | string | null): void;
}>();

const languages: Ref<Language[] | null> = ref<Language[] | null>(null);

watchEffect(async () => {
    const response = (await fetchLanguages()) as {
        languages: Language[];
        request_language: string;
    };

    languages.value = response.languages;
});

function onUpdateModelValue(updatedValue: string | null) {
    if (shouldEmitSimplifiedValue) {
        emit("update:value", updatedValue);
    } else {
        const updatedDisplayValue =
            languages.value?.find(
                (option: Language) => option.code === updatedValue,
            )?.name || "";

        emit("update:value", {
            display_value: updatedDisplayValue,
            node_value: updatedValue,
            details: [],
        });
    }
}
</script>

<template>
    <Select
        option-value="code"
        option-label="name"
        :options="languages as Language[]"
        :placeholder="cardXNodeXWidgetData.config.placeholder"
        :fluid="true"
        :model-value="aliasedNodeData?.node_value"
        @update:model-value="onUpdateModelValue($event)"
    />
</template>
