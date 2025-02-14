<script setup lang="ts">
import dayjs from "dayjs";
import { onMounted, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";

import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import { fetchWidgetConfiguration } from "@/arches_component_lab/widgets/api.ts";
import { convertISO8601DatetimeFormatToPrimevueDatetimeFormat } from "@/arches_component_lab/widgets/utils.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    graphSlug: string;
    nodeAlias: string;
    initialValue: Date | undefined;
    mode: WidgetMode;
}>();

const isLoading = ref(true);
const configuration = ref();

onMounted(async () => {
    const widgetConfiguration = await fetchWidgetConfiguration(
        props.graphSlug,
        props.nodeAlias,
    );

    configuration.value = {
        ...widgetConfiguration,
        datePickerDisplayConfiguration:
            convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
                widgetConfiguration.dateFormat,
            ),
    };

    isLoading.value = false;
});
</script>

<template>
    <ProgressSpinner
        v-if="isLoading"
        style="width: 2em; height: 2em"
    />

    <template v-else>
        <label>{{ configuration.label }}</label>

        <DateWidgetEditor
            v-if="props.mode === EDIT"
            :initial-value="dayjs(props.initialValue).toDate()"
            :graph-slug="props.graphSlug"
            :node-alias="props.nodeAlias"
            :configuration="configuration"
        />
        <DateWidgetViewer
            v-else-if="props.mode === VIEW"
            :value="dayjs(props.initialValue).toDate()"
            :configuration="configuration"
        />
    </template>
</template>
