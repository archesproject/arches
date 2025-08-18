<script setup lang="ts">
import { ref, watch, watchEffect } from "vue";
import { useGettext } from "vue3-gettext";

import Editor from "primevue/editor";
import Select from "primevue/select";

import { fetchLanguages } from "@/arches_component_lab/widgets/api.ts";

import type {
    StringCardXNodeXWidgetData,
    Language,
} from "@/arches_component_lab/types.ts";
import type { StringValue } from "@/arches_component_lab/datatypes/string/types.ts";
import FocusController from "./components/FocusController.vue";

const { $gettext } = useGettext();

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData: StringCardXNodeXWidgetData;
    aliasedNodeData: StringValue;
}>();

const emit = defineEmits<{
    (event: "update:value", updatedValue: StringValue): void;
}>();

const languages = ref<Language[]>([]);
const selectedLanguage = ref<Language>();
const managedNodeValue = ref<StringValue["node_value"]>();
const singleInputValue = ref<string>("");

watchEffect(async () => {
    const response = (await fetchLanguages()) as {
        languages: Language[];
        request_language: string;
    };

    languages.value = response.languages;

    selectedLanguage.value =
        languages.value.find((lang) => {
            return lang.code === response.request_language;
        }) ?? response.languages[0];
});

watch(languages, () => {
    const workingObject = { ...aliasedNodeData.node_value };

    for (const knownLanguage of languages.value) {
        if (!workingObject[knownLanguage.code]) {
            workingObject[knownLanguage.code] = {
                value: "",
                direction: knownLanguage.default_direction,
            };
        }
    }

    managedNodeValue.value = workingObject;
});

watch(selectedLanguage, () => {
    if (selectedLanguage.value && managedNodeValue.value) {
        singleInputValue.value =
            managedNodeValue.value[selectedLanguage.value.code].value ?? "";
    } else {
        singleInputValue.value = "";
    }
});

function onUpdateModelValue(updatedValue: string | undefined) {
    if (updatedValue === undefined) {
        updatedValue = "";
    }

    emit("update:value", {
        display_value: updatedValue,
        node_value: {
            ...managedNodeValue.value,
            [selectedLanguage.value!.code]: {
                value: updatedValue,
                direction: selectedLanguage.value!.default_direction,
            },
        },
        details: [],
    });
}
</script>

<template>
    <div style="display: flex; flex-direction: column; row-gap: 0.5rem">
        <Select
            v-model="selectedLanguage"
            :aria-label="$gettext('Select language for node value')"
            :options="languages"
            :option-label="(lang: Language) => `${lang.name} (${lang.code})`"
            :placeholder="$gettext('Language')"
            :pt="{
                label: { style: { fontSize: '1rem' } },
                optionLabel: { style: { fontSize: '1rem' } },
            }"
        />
        <FocusController :node-alias="cardXNodeXWidgetData.node.alias">
            <Editor
                :fluid="true"
                :model-value="singleInputValue"
                :placeholder="cardXNodeXWidgetData.config.placeholder ?? ''"
                :required="cardXNodeXWidgetData.node.isrequired"
                @update:model-value="onUpdateModelValue($event)"
            />
        </FocusController>
    </div>
</template>
