<script setup lang="ts">
import { computed, onMounted, ref, watchEffect } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "openvue/inputtext";
import Message from "openvue/message";
import Select from "openvue/select";
import Textarea from "openvue/textarea";

import { MULTILINE_RENDER_CONTEXT } from "@/arches_vue_components/widgets/TextWidget/constants.ts";
import { buildStringAliasedNodeData } from "@/arches_vue_components/datatypes/string/utils.ts";
import { useLanguageStore } from "@/arches_vue_components/stores/useLanguageStore.ts";

import type {
    StringCardXNodeXWidgetData,
    Language,
} from "@/arches_vue_components/types.ts";
import type {
    LanguageValue,
    StringAliasedNodeData,
} from "@/arches_vue_components/datatypes/string/types.ts";

const {
    cardXNodeXWidgetData = undefined,
    aliasedNodeData,
    renderContext = undefined,
} = defineProps<{
    cardXNodeXWidgetData?: StringCardXNodeXWidgetData;
    aliasedNodeData: StringAliasedNodeData | null;
    renderContext?: string;
}>();

const initialNodeValue = aliasedNodeData?.node_value;

const emit = defineEmits<{
    (
        event: "update:aliasedNodeData",
        updatedValue: StringAliasedNodeData,
    ): void;
    (event: "ready"): void;
}>();

const { $gettext } = useGettext();
const languageStore = useLanguageStore();

const selectedLanguage = ref<Language | undefined>(resolveInitialLanguage());
const managedNodeValue = ref<Record<string, LanguageValue>>();
const singleInputValue = ref<string>();
const fetchError = ref<string | null>(null);

const languages = computed(() => languageStore.languages);

watchEffect(async () => {
    if (selectedLanguage.value) {
        return;
    }
    try {
        await languageStore.fetchAllLanguages();
        selectedLanguage.value = resolveInitialLanguage();
    } catch (error) {
        fetchError.value =
            error instanceof Error ? error.message : String(error);
    } finally {
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

onMounted(() => {
    if (selectedLanguage.value) {
        emit("ready");
    }
});

function resolveInitialLanguage(): Language | undefined {
    const nonEmptyLanguageCodes = Object.entries(initialNodeValue ?? {})
        .filter(([, language]) => language.value !== "")
        .map(([code]) => code);
    let targetLanguageCode = languageStore.requestLanguageCode;
    if (nonEmptyLanguageCodes.length === 1) {
        targetLanguageCode = nonEmptyLanguageCodes[0];
    }
    return (
        languageStore.languages.find(
            (language: Language) => language.code === targetLanguageCode,
        ) ??
        languageStore.languages.find(
            (language: Language) => language.isdefault,
        ) ??
        languageStore.languages[0]
    );
}

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
    <Message
        v-if="fetchError"
        severity="error"
        size="small"
        variant="simple"
    >
        <span>
            {{
                $gettext(
                    "Unable to load languages: %{message}",
                    { message: fetchError },
                    true,
                )
            }}
        </span>
    </Message>
    <div
        v-else
        class="widget-language-inputs"
    >
        <Select
            v-model="selectedLanguage"
            class="language-selector"
            :aria-label="$gettext('Select language for node value')"
            :options="languages"
            :option-label="(lang: Language) => `${lang.name} (${lang.code})`"
            :placeholder="$gettext('Language')"
        />
        <Textarea
            v-if="renderContext === MULTILINE_RENDER_CONTEXT"
            :auto-resize="true"
            :fluid="true"
            :maxlength="cardXNodeXWidgetData?.config.maxLength ?? undefined"
            :model-value="singleInputValue"
            :placeholder="cardXNodeXWidgetData?.config.placeholder"
            :pt="{ root: { id: cardXNodeXWidgetData?.node.alias } }"
            :required="cardXNodeXWidgetData?.node.isrequired"
            rows="4"
            @update:model-value="onUpdateModelValue($event)"
        />
        <InputText
            v-else
            type="text"
            :fluid="true"
            :maxlength="cardXNodeXWidgetData?.config.maxLength ?? undefined"
            :model-value="singleInputValue"
            :placeholder="cardXNodeXWidgetData?.config.placeholder"
            :pt="{ root: { id: cardXNodeXWidgetData?.node.alias } }"
            :required="cardXNodeXWidgetData?.node.isrequired"
            @update:model-value="onUpdateModelValue($event)"
        />
    </div>
</template>

<style scoped>
.widget-language-inputs {
    display: flex;
    column-gap: 0.5rem;
}
</style>

<style>
.p-select-options,
.p-select-label,
.p-select-overlay {
    font-size: 1rem;
}
</style>
