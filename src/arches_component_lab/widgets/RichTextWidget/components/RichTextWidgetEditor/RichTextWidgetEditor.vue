<script setup lang="ts">
import { ref, watchEffect } from "vue";

import { useGettext } from "vue3-gettext";
import Editor from "primevue/editor";
import Select from "primevue/select";

import FocusController from "@/arches_component_lab/widgets/RichTextWidget/components/RichTextWidgetEditor/components/FocusController.vue";

import { fetchLanguages } from "@/arches_component_lab/widgets/api.ts";
import { buildStringAliasedNodeData } from "@/arches_component_lab/datatypes/string/utils.ts";

import type {
    StringCardXNodeXWidgetData,
    Language,
} from "@/arches_component_lab/types.ts";
import type {
    LanguageValue,
    StringAliasedNodeData,
} from "@/arches_component_lab/datatypes/string/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: StringCardXNodeXWidgetData;
    aliasedNodeData: StringAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: StringAliasedNodeData,
    ): void;
    (event: "initialized", updatedValue: StringAliasedNodeData): void;
}>();

const { $gettext } = useGettext();

const languages = ref<Language[]>([]);
const selectedLanguage = ref<Language>();
const managedNodeValue = ref<Record<string, LanguageValue>>();
const singleInputValue = ref<string>("");
const hasInitialized = ref(false);

watchEffect(async () => {
    const response = (await fetchLanguages()) as {
        languages: Language[];
        request_language: string;
    };

    languages.value = response.languages;

    selectedLanguage.value =
        languages.value.find((lang: Language) => {
            return lang.code === response.request_language;
        }) ??
        response.languages.find((lang: Language) => lang.isdefault) ??
        response.languages[0];

    if (!hasInitialized.value && selectedLanguage.value) {
        hasInitialized.value = true;
        emit(
            "initialized",
            aliasedNodeData ??
                buildStringAliasedNodeData(
                    (managedNodeValue.value ?? {}) as Record<
                        string,
                        LanguageValue
                    >,
                    selectedLanguage.value.code,
                ),
        );
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
