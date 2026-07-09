<script setup lang="ts">
import { useTemplateRef, watchEffect } from "vue";

import { FormField, type FormFieldResolverOptions } from "@primevue/forms";
import Message from "primevue/message";

import type { AliasedNodeData } from "@/arches_component_lab/types.ts";

type FormFieldType = {
    field: {
        states: {
            dirty: boolean;
            pristine: boolean;
            touched: boolean;
        };
        errors: Array<{ message: string }>;
        props: {
            onChange: (event: { value: AliasedNodeData }) => void;
        };
    };
};

const { isDirty, nodeAlias, initialValue } = defineProps<{
    isDirty: boolean;
    nodeAlias: string;
    initialValue: AliasedNodeData | null;
}>();

const emit = defineEmits<{
    (e: "update:isDirty", dirty: boolean): void;
}>();

const formFieldRef = useTemplateRef<FormFieldType>("formField");

watchEffect(() => {
    if (isDirty) {
        markFormFieldAsDirty();
    }
});

function markFormFieldAsDirty() {
    if (!formFieldRef.value) {
        return;
    }

    formFieldRef.value.field.states.dirty = true;
    formFieldRef.value.field.states.pristine = false;
    formFieldRef.value.field.states.touched = true;
}

function resolver(updatedNodeValue: FormFieldResolverOptions) {
    const errors = validate(updatedNodeValue);
    return errors.length ? { errors } : {};
}

function validate(
    _value: FormFieldResolverOptions,
): Array<{ message: string }> {
    return [];
}

function onUpdateAliasedNodeData(aliasedNodeData: AliasedNodeData) {
    formFieldRef.value?.field?.props?.onChange({
        value: aliasedNodeData,
    });

    emit("update:isDirty", true);
}
</script>

<template>
    <slot :on-update-aliased-node-data="onUpdateAliasedNodeData" />

    <FormField
        v-if="initialValue"
        ref="formField"
        v-slot="$field"
        :name="nodeAlias"
        :resolver="resolver"
        :initial-value="initialValue"
    >
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
