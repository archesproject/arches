<script setup lang="ts">
import { ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { URL, URLValue } from "@/arches_component_lab/datatypes/url/types";

const { $gettext } = useGettext();

const {
    cardXNodeXWidgetData,
    aliasedNodeData,
    shouldEmitSimplifiedValue = false,
} = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    aliasedNodeData: URLValue | null;
    shouldEmitSimplifiedValue?: boolean;
}>();

const urlLabel = ref(aliasedNodeData!.node_value?.url_label || "");
const url = ref(aliasedNodeData!.node_value?.url || "");

const emit = defineEmits<{
    (event: "update:value", updatedValue: URLValue | URL): void;
}>();

function onUpdateURLValue(updatedValue: string | undefined) {
    if (updatedValue === undefined) {
        updatedValue = "";
    }
    url.value = updatedValue;
    updateValue();
}

function onUpdateURLLabelValue(updatedValue: string | undefined) {
    if (updatedValue === undefined) {
        updatedValue = "";
    }
    urlLabel.value = updatedValue;
    updateValue();
}

function updateValue() {
    let displayValue;
    if (urlLabel.value) {
        displayValue = `${urlLabel.value}(${url.value})`;
    } else {
        displayValue = url.value;
    }
    const formattedValue = {
        url: url.value,
        url_label: urlLabel.value,
    };
    if (shouldEmitSimplifiedValue) {
        emit("update:value", formattedValue);
    } else {
        emit("update:value", {
            display_value: displayValue,
            node_value: formattedValue,
            details: [],
        });
    }
}
</script>

<template>
    <div>{{ $gettext("URL Label") }}</div>
    <InputText
        type="text"
        :fluid="true"
        :model-value="urlLabel"
        :placeholder="$gettext('Enter URL Label...')"
        @update:model-value="onUpdateURLLabelValue($event)"
    />
    <div>{{ $gettext("URL") }}</div>
    <InputText
        type="text"
        required="true"
        :fluid="true"
        :model-value="url"
        :pt="{ root: { id: cardXNodeXWidgetData.node.alias } }"
        :placeholder="$gettext('Enter URL...')"
        @update:model-value="onUpdateURLValue($event)"
    />
    <div>{{ $gettext("Preview") }}</div>
    <div>
        <a
            v-if="url"
            :href="url"
            tabindex="-1"
            target="_blank"
            rel="noopener noreferrer"
            >{{ urlLabel || url }}</a
        >
        <span v-else>{{ urlLabel }}</span>
    </div>
</template>
