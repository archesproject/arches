<script setup lang="ts">
import dayjs from "dayjs";
import { onMounted, ref } from "vue";

import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import { fetchWidgetConfiguration } from "@/arches_component_lab/widgets/api.ts";
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
const configuration = ref();
const configurationError = ref();

onMounted(async () => {
    try {
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
    } catch (error) {
        configurationError.value = error;
    } finally {
        isLoading.value = false;
    }
});
</script>

<template>
    <ProgressSpinner
        v-if="isLoading"
        style="width: 2em; height: 2em"
    />

    <template v-else>
        <label v-if="props.showLabel">{{ configuration.label }}</label>

        <DateWidgetEditor
            v-if="props.mode === EDIT"
            :initial-value="
                props.initialValue &&
                dayjs(props.initialValue).toDate().toString()
            "
            :graph-slug="props.graphSlug"
            :node-alias="props.nodeAlias"
            :configuration="configuration"
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
    <Message
        v-if="configurationError"
        severity="error"
        size="small"
    >
        {{ configurationError.message }}
    </Message>
</template>
