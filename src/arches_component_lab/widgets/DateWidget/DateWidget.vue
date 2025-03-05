<script setup lang="ts">
import dayjs from "dayjs";
import { onMounted, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";

import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import {
    fetchWidgetData,
    fetchNodeData,
} from "@/arches_component_lab/widgets/api.ts";
import { convertISO8601DatetimeFormatToPrimevueDatetimeFormat } from "@/arches_component_lab/widgets/utils.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        initialValue: string | undefined;
        nodeAlias: string;
        graphSlug: string;
        showLabel?: boolean;
    }>(),
    {
        showLabel: true,
    },
);

const isLoading = ref(true);
const nodeData = ref();
const widgetData = ref();

onMounted(async () => {
    nodeData.value = await fetchNodeData(
        props.graphSlug,
        props.nodeAlias,
    );

    const widget = await fetchWidgetData(
        props.graphSlug,
        props.nodeAlias,
    );
    widget.config.datePickerDisplayConfiguration = convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
        widget.config.dateFormat,
    );
    widgetData.value = widget;

    isLoading.value = false;
});
</script>

<template>
    <ProgressSpinner
        v-if="isLoading"
        style="width: 2em; height: 2em"
    />

    <template v-else>
        <label v-if="props.showLabel">
            <span>{{ widgetData.label }}</span>
            <span v-if="nodeData.isrequired && props.mode === EDIT">*</span>
        </label>

        <DateWidgetEditor
            v-if="props.mode === EDIT"
            :initial-value="
                props.initialValue &&
                dayjs(props.initialValue).toDate().toString()
            "
            :graph-slug="props.graphSlug"
            :node-alias="props.nodeAlias"
            :configuration="widgetData.config"
        />
        <DateWidgetViewer
            v-else-if="props.mode === VIEW"
            :value="
                props.initialValue &&
                dayjs(props.initialValue).toDate().toString()
            "
            :configuration="widgetData.config"
        />
    </template>
</template>
