<script setup lang="ts">
import dayjs from "dayjs";

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
            datePickerDisplayConfiguration: {
                dateFormat: string;
                shouldShowTime: boolean;
            };
        };
    };
}>();

function resolver(e: FormFieldResolverOptions) {
    validate(e);

    return {
        values: {
            [props.nodeAlias]: dayjs(e.value).format(
                props.widgetData.config.dateFormat,
            ),
        },
    };
}

function validate(e: FormFieldResolverOptions) {
    console.log("validate", e);
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
            :date-format="
                props.widgetData.config.datePickerDisplayConfiguration
                    .dateFormat
            "
            :fluid="true"
            :show-icon="true"
            :show-time="
                props.widgetData.config.datePickerDisplayConfiguration
                    .shouldShowTime
            "
            :show-seconds="
                props.widgetData.config.datePickerDisplayConfiguration
                    .shouldShowTime
            "
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
