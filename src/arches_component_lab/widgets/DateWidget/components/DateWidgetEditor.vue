<script setup lang="ts">
import { ref, onMounted } from "vue";

import dayjs from "dayjs";
import { convertISO8601DatetimeFormatToPrimevueDatetimeFormat } from "@/arches_component_lab/widgets/utils.ts";

import DatePicker from "primevue/datepicker";
import Message from "primevue/message";

import { FormField } from "@primevue/forms";
import type { FormFieldResolverOptions } from "@primevue/forms";

const props = defineProps<{
    initialValue: string | null | undefined;
    graphSlug: string;
    nodeAlias: string;
    widgetData: {
        config: {
            dateFormat: string;
        };
    };
}>();

const shouldShowTime = ref(false);
const dateFormat = ref();

onMounted(() => {
    const convertedDateFormat =
        convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
            props.widgetData.config.dateFormat,
        );

    dateFormat.value = convertedDateFormat.dateFormat;
    shouldShowTime.value = convertedDateFormat.shouldShowTime;
});

function resolver(e: FormFieldResolverOptions) {
    validate(e);

    return {
        values: {
            [props.nodeAlias]: formatDate(e.value),
        },
    };
}

function validate(e: FormFieldResolverOptions) {
    console.log("validate", e);
}

function formatDate(date: Date | null): string | null {
    if (!date) {
        return null;
    }

    return dayjs(date).format(props.widgetData.config.dateFormat);
}
</script>

<template>
    <FormField
        ref="formFieldRef"
        v-slot="$field"
        :name="props.nodeAlias"
        :initial-value="props.initialValue"
        :resolver="resolver"
    >
        <DatePicker
            icon-display="input"
            :date-format="dateFormat"
            :fluid="true"
            :show-time="shouldShowTime"
            :show-seconds="shouldShowTime"
            :show-icon="true"
            @keydown.enter.prevent
        />
        <Message
            v-for="error in $field.errors"
            :key="error.message"
            severity="error"
            size="small"
        >
            {{ error.message }}
        </Message>
    </FormField>
</template>
