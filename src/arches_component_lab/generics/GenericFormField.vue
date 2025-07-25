<script setup lang="ts">
import { computed, useSlots, useTemplateRef } from "vue";

import { FormField } from "@primevue/forms";
import Message from "primevue/message";

import type { FormFieldResolverOptions } from "@primevue/forms";

const slots = useSlots();

const props = defineProps<{
    nodeAlias: string;
    validateValue?: (event: unknown) => void;
    transformValueForForm?: (
        event: FormFieldResolverOptions,
    ) => unknown | null | undefined;
}>();

const emit = defineEmits<{
    (e: "update:value", newValue: unknown | null | undefined): void;
    (e: "update:isDirty", dirty: boolean): void;
}>();

const formFieldRef = useTemplateRef("formField");

const derivedInitialValue = computed(() => {
    const defaultSlotNodes = slots.default?.();
    const firstVNodeProps = defaultSlotNodes?.[0].props;

    if (!firstVNodeProps) {
        return null;
    }

    return (
        firstVNodeProps["value"] ||
        firstVNodeProps["model-value"] ||
        firstVNodeProps["modelValue"]
    );
});

function internalValidate(event: unknown) {
    if (props.validateValue) {
        props.validateValue(event);
    } else {
        console.log("validateValue", event);
    }
}

function internalResolver(event: FormFieldResolverOptions) {
    let value;

    if (props.transformValueForForm) {
        value = props.transformValueForForm(event);
    } else {
        value = event.value;
    }

    internalValidate(value);

    // @ts-expect-error This is a bug with PrimeVue types
    emit("update:isDirty", Boolean(formFieldRef.value!.fieldAttrs.dirty));
    emit("update:value", value);

    return value;
}
</script>

<template>
    <FormField
        ref="formField"
        v-slot="$field"
        :name="nodeAlias"
        :resolver="internalResolver"
        :initial-value="derivedInitialValue"
    >
        <slot v-bind="$field" />

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
