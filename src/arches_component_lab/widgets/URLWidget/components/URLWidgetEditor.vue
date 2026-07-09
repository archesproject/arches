<script setup lang="ts">
import { onMounted, ref } from "vue";

import { useGettext } from "vue3-gettext";
import InputText from "primevue/inputtext";

import { buildURLAliasedNodeData } from "@/arches_component_lab/datatypes/url/utils.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { URLAliasedNodeData } from "@/arches_component_lab/datatypes/url/types";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData: URLAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (event: "update:aliasedNodeData", updatedValue: URLAliasedNodeData): void;
    (event: "initialized", updatedValue: URLAliasedNodeData): void;
}>();

const { $gettext } = useGettext();

const urlLabel = ref(aliasedNodeData?.node_value?.url_label ?? "");
const url = ref(aliasedNodeData?.node_value?.url ?? "");

onMounted(() => {
    emit(
        "initialized",
        aliasedNodeData ??
            buildURLAliasedNodeData({
                url: url.value,
                url_label: urlLabel.value,
            }),
    );
});

function onUpdateURLValue(updatedValue: string | undefined) {
    url.value = updatedValue ?? "";
    updateValue();
}

function onUpdateURLLabelValue(updatedValue: string | undefined) {
    urlLabel.value = updatedValue ?? "";
    updateValue();
}

function updateValue() {
    const newNodeValue = { url: url.value, url_label: urlLabel.value };
    emit("update:aliasedNodeData", buildURLAliasedNodeData(newNodeValue));
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
        :pt="{ root: { id: cardXNodeXWidgetData?.node.alias } }"
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
