<script setup lang="ts">
import dayjs from "dayjs";
import { onMounted, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";

import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import {
    fetchWidget,
    fetchNode,
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
const nodeRef = ref();
const widgetRef = ref();

onMounted(async () => {
    nodeRef.value = await fetchNode(
        props.graphSlug,
        props.nodeAlias,
    );

    const widget = await fetchWidget(
        props.graphSlug,
        props.nodeAlias,
    );
    widget.config.datePickerDisplayConfiguration = convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
        widget.config.dateFormat,
    );
    widgetRef.value = widget;

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
            <span>{{ widgetRef.label }}</span>
            <span v-if="nodeRef.isrequired && props.mode === EDIT">*</span>
        </label>

        <DateWidgetEditor
            v-if="props.mode === EDIT"
            :initial-value="
                props.initialValue &&
                dayjs(props.initialValue).toDate().toString()
            "
            :graph-slug="props.graphSlug"
            :node-alias="props.nodeAlias"
            :configuration="widgetRef.config"
        />
        <DateWidgetViewer
            v-else-if="props.mode === VIEW"
            :value="
                props.initialValue &&
                dayjs(props.initialValue).toDate().toString()
            "
            :configuration="configuration"
        />
    </template>
</template>
