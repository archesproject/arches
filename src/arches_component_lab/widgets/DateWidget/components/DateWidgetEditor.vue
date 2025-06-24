<script setup lang="ts">
import { ref, onMounted } from "vue";

import dayjs from "dayjs";
import { convertISO8601DatetimeFormatToPrimevueDatetimeFormat } from "@/arches_component_lab/widgets/utils.ts";

import DatePicker from "primevue/datepicker";
import Message from "primevue/message";

import { FormField } from "@primevue/forms";

import type { FormFieldResolverOptions } from "@primevue/forms";
import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";

const props = defineProps<{
    value: string | null | undefined;
    graphSlug: string;
    nodeAlias: string;
    cardXNodeXWidgetData: CardXNodeXWidget & {
        config: {
            dateFormat: string;
            datePickerDisplayConfiguration: {
                dateFormat: string;
                shouldShowTime: boolean;
            };
        };
    };
}>();

const emit = defineEmits<{
    (event: "update:value", value: string | null): void;
}>();

const shouldShowTime = ref(false);
const dateFormat = ref();

onMounted(() => {
    const convertedDateFormat =
        convertISO8601DatetimeFormatToPrimevueDatetimeFormat(
            props.cardXNodeXWidgetData.config.dateFormat,
        );

    dateFormat.value = convertedDateFormat.dateFormat;
    shouldShowTime.value = convertedDateFormat.shouldShowTime;
});

function resolver(e: FormFieldResolverOptions) {
    validate(e);

    emit("update:value", e.value);

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

    return dayjs(date).format(props.cardXNodeXWidgetData.config.dateFormat);
}
</script>

<template>
    <FormField
        ref="formFieldRef"
        v-slot="$field"
        :name="props.nodeAlias"
        :initial-value="props.value"
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
