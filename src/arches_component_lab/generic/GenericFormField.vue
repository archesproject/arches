<script setup lang="ts">
import { useTemplateRef } from "vue";

import { FormField } from "@primevue/forms";
import Message from "primevue/message";

import type { FormFieldResolverOptions } from "@primevue/forms";

const { nodeAlias, initialValue, validate, resolver } = defineProps<{
    nodeAlias: string;
    initialValue: unknown | null | undefined;
    validate?: (event: unknown) => void;
    resolver?: (event: FormFieldResolverOptions) => unknown | null | undefined;
}>();

const emit = defineEmits<{
    (e: "update:value", newValue: unknown | null | undefined): void;
    (e: "update:isDirty", dirty: boolean): void;
}>();

const formFieldRef = useTemplateRef("formField");

function internalValidate(event: unknown) {
    if (validate) {
        validate(event);
    } else {
        console.log("validate", event);
    }
}

function internalResolver(event: FormFieldResolverOptions) {
    let resolverResult;

    if (resolver) {
        resolverResult = resolver(event);
    } else {
        resolverResult = event.value;
    }

    internalValidate(resolverResult);

    // @ts-expect-error This is a bug with PrimeVue types
    emit("update:isDirty", Boolean(formFieldRef.value!.fieldAttrs.dirty));
    emit("update:value", resolverResult);
    // emit("update:value", event.value);

    return resolverResult;
}
</script>

<template>
    <FormField
        ref="formField"
        v-slot="$field"
        :name="nodeAlias"
        :initial-value="initialValue"
        :resolver="internalResolver"
    >
        <slot v-bind="$field"></slot>

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
