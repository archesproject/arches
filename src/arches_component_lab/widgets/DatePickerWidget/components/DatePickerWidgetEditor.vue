<script setup lang="ts">
import { computed, onMounted, ref, watchEffect } from "vue";

import { debounce } from "es-toolkit/function";
import DatePicker from "primevue/datepicker";

import {
    convertISO8601DatetimeFormatToPrimevueDatetimeFormat,
    convertViewMode,
} from "@/arches_component_lab/widgets/DatePickerWidget/utils.ts";
import {
    buildDateAliasedNodeData,
    formatDate,
} from "@/arches_component_lab/datatypes/date/utils.ts";

import type {
    DateAliasedNodeData,
    DateDatatypeCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/date/types.ts";

const { cardXNodeXWidgetData, aliasedNodeData } = defineProps<{
    cardXNodeXWidgetData?: DateDatatypeCardXNodeXWidgetData;
    aliasedNodeData: DateAliasedNodeData | null;
}>();

const emit = defineEmits<{
    (event: "update:aliasedNodeData", updatedValue: DateAliasedNodeData): void;
    (event: "initialized", updatedValue: DateAliasedNodeData): void;
}>();

const shouldShowTime = ref(false);
const dateFormat = ref();

const viewMode = computed(() => {
    return convertViewMode(cardXNodeXWidgetData?.config?.viewMode ?? "days");
});

const modelDate = computed(() => {
    const nodeValue = aliasedNodeData?.node_value ?? null;
    if (!nodeValue) {
        return null;
    }
    if (shouldShowTime.value) {
        return new Date(nodeValue);
    }
    const incomingDate = new Date(nodeValue);
    const day = incomingDate.getUTCDate();
    const month = incomingDate.getUTCMonth();
    const year = incomingDate.getUTCFullYear();
    return new Date(year, month, day);
});

watchEffect(() => {
    const convertedDateFormat =
        convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
            cardXNodeXWidgetData?.node.config.dateFormat ?? "",
        );

    dateFormat.value = convertedDateFormat.dateFormat;
    shouldShowTime.value = convertedDateFormat.shouldShowTime;
});

onMounted(() => {
    emit("initialized", aliasedNodeData ?? buildDateAliasedNodeData(null));
});

const onUpdateModelValue = debounce(function onUpdateModelValueDebounced(
    updatedValue: string,
) {
    if (!updatedValue) {
        emit("update:aliasedNodeData", buildDateAliasedNodeData(null));
        return;
    }

    const date = new Date(updatedValue);

    try {
        const formattedDate = formatDate(
            date,
            cardXNodeXWidgetData?.node.config.dateFormat ?? "",
        );
        emit("update:aliasedNodeData", buildDateAliasedNodeData(formattedDate));
    } catch (_error) {
        emit("update:aliasedNodeData", buildDateAliasedNodeData(updatedValue));
    }
}, 900);
</script>

<template>
    <DatePicker
        icon-display="input"
        :date-format="dateFormat"
        :fluid="true"
        :input-id="cardXNodeXWidgetData?.node.alias"
        :manual-input="true"
        :show-clear="true"
        :model-value="modelDate"
        :show-time="shouldShowTime"
        :show-seconds="shouldShowTime"
        :show-icon="true"
        :view="viewMode"
        @update:model-value="onUpdateModelValue($event as unknown as string)"
    />
</template>
