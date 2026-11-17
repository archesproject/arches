<script setup lang="ts">
import { ref, watch, watchEffect } from "vue";

import { useGettext } from "vue3-gettext";
import Editor from "openvue/editor";
import Select from "openvue/select";

import FocusController from "@/arches_vue_components/widgets/RichTextWidget/components/RichTextWidgetEditor/components/FocusController.vue";

import { fetchLanguages } from "@/arches_vue_components/widgets/api.ts";
import {
    buildStringAliasedNodeData,
    getOnlyFilledLanguageCode,
} from "@/arches_vue_components/datatypes/string/utils.ts";

import type {
    StringCardXNodeXWidgetData,
    Language,
} from "@/arches_vue_components/types.ts";
import type {
    LanguageValue,
    StringAliasedNodeData,
} from "@/arches_vue_components/datatypes/string/types.ts";

const { cardXNodeXWidgetData = undefined, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: StringCardXNodeXWidgetData;
    aliasedNodeData: StringAliasedNodeData | null;
}>();

const initialNodeValue = aliasedNodeData?.node_value;

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: StringAliasedNodeData,
    ): void;
    (event: "update:selectedLanguage", languageCode: string): void;
    (event: "ready"): void;
}>();

const { $gettext } = useGettext();

const languages = ref<Language[]>([]);
const selectedLanguage = ref<Language>();
const managedNodeValue = ref<Record<string, LanguageValue>>();
const singleInputValue = ref<string>("");

watchEffect(async () => {
    const response = (await fetchLanguages()) as {
        languages: Language[];
        request_language: string;
    };

    languages.value = response.languages;

    const targetLanguageCode =
        getOnlyFilledLanguageCode(initialNodeValue) ??
        response.request_language;

    selectedLanguage.value =
        languages.value.find((lang: Language) => {
            return lang.code === targetLanguageCode;
        }) ??
        response.languages.find((lang: Language) => lang.isdefault) ??
        response.languages[0];

    if (selectedLanguage.value) {
        emit("ready");
    }
});

watchEffect(() => {
    const workingObject = { ...(aliasedNodeData?.node_value ?? {}) };
    for (const knownLanguage of languages.value) {
        if (!workingObject[knownLanguage.code]) {
            workingObject[knownLanguage.code] = {
                value: "",
                direction: knownLanguage.default_direction,
            };
        }
    }
    managedNodeValue.value = workingObject;

    if (selectedLanguage.value && managedNodeValue.value) {
        singleInputValue.value =
            managedNodeValue.value[selectedLanguage.value.code].value ?? "";
    } else {
        singleInputValue.value = "";
    }
});

watch(
    selectedLanguage,
    (language) => {
        if (language) {
            emit("update:selectedLanguage", language.code);
        }
    },
    { immediate: true },
);

function onUpdateModelValue(updatedValue: string | undefined) {
    if (updatedValue === undefined) {
        updatedValue = "";
    }
    const newNodeValue = {
        ...managedNodeValue.value,
        [selectedLanguage.value!.code]: {
            value: updatedValue,
            direction: selectedLanguage.value!.default_direction,
        },
    };
    emit(
        "update:aliasedNodeData",
        buildStringAliasedNodeData(newNodeValue, selectedLanguage.value!.code),
    );
}
</script>

<template>
    <div class="widget-language-inputs">
        <Select
            v-model="selectedLanguage"
            class="language-selector"
            :aria-label="$gettext('Select language for node value')"
            :options="languages"
            :option-label="(lang: Language) => `${lang.name} (${lang.code})`"
            :placeholder="$gettext('Language')"
        />
        <FocusController :node-alias="cardXNodeXWidgetData?.node.alias ?? ''">
            <Editor
                :fluid="true"
                :model-value="singleInputValue"
                :placeholder="cardXNodeXWidgetData?.config.placeholder ?? ''"
                :required="cardXNodeXWidgetData?.node.isrequired"
                @update:model-value="onUpdateModelValue($event)"
            />
        </FocusController>
    </div>
</template>

<style scoped>
.widget-language-inputs {
    display: flex;
    flex-direction: column;
    row-gap: 0.5rem;
}
</style>

<style>
.p-select-options,
.p-select-label,
.p-select-overlay {
    font-size: 1rem;
}
</style>
