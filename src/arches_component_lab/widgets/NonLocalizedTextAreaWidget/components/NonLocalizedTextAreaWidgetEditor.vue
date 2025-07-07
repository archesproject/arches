<script setup lang="ts">
import { useTemplateRef } from "vue";

import Message from "primevue/message";
import Textarea from "primevue/textarea";

import { FormField } from "@primevue/forms";

import type { FormFieldResolverOptions } from "@primevue/forms";

const props = defineProps<{
    nodeAlias: string;
    value: string | null | undefined;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);

const formFieldRef = useTemplateRef("formField");

function resolver(event: FormFieldResolverOptions) {
    validate(event);

    // @ts-expect-error This is a bug with PrimeVue types
    emit("update:isDirty", Boolean(formFieldRef.value!.fieldAttrs.dirty));
    emit("update:value", event.value);

    return {
        values: { [props.nodeAlias]: event.value },
    };
}

function validate(e: FormFieldResolverOptions) {
    console.log("validate", e);
}
</script>

<template>
    <FormField
        ref="formField"
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
