<script setup lang="ts">
import Textarea from "primevue/textarea";
import Message from "primevue/message";

import { FormField, type FormFieldResolverOptions } from "@primevue/forms";

const props = defineProps<{
    value: string | null | undefined;
    nodeAlias: string;
    graphSlug: string;
}>();

function resolver(e: FormFieldResolverOptions) {
    validate(e);

    return {
        values: { [props.nodeAlias]: e.value },
    };
}

function validate(e: FormFieldResolverOptions) {
    console.log("validate", e);
}
</script>

<template>
    <FormField
        v-slot="$field"
        :name="props.nodeAlias"
        :initial-value="props.value"
        :resolver="resolver"
    >
        <Textarea
            :fluid="true"
            :draggable="true"
            :rows="12"
            style="resize: vertical"
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
