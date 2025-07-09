<script setup lang="ts">
import { useTemplateRef } from "vue";

import ToggleSwitch from "primevue/toggleswitch";
import RadioButton from "primevue/radiobutton";
import RadioButtonGroup from "primevue/radiobuttongroup";
import Message from "primevue/message";
import { FormField, type FormFieldResolverOptions } from "@primevue/forms";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";

const emit = defineEmits(["update:isDirty", "update:value"]);

const formFieldRef = useTemplateRef("formField");

const props = defineProps<{
    nodeAlias: string;
    cardXNodeXWidgetData?: CardXNodeXWidget;
    graphSlug: string;
    value: boolean | null | undefined;
}>();

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

console.log(
    "BooleanWidgetEditor props",
    props.cardXNodeXWidgetData.widget.name,
);
</script>

<template>
    <FormField
        ref="formField"
        v-slot="$field"
        :name="props.nodeAlias"
        :initial-value="props.value.interchange_value"
        :resolver="resolver"
    >
        <ToggleSwitch
            v-if="props.cardXNodeXWidgetData?.widget?.name === 'switch-widget'"
            :id="`${props.graphSlug}-${props.nodeAlias}-input`"
            :modelValue="props.value.interchange_value"
            :fluid="true"
        />

        <RadioButtonGroup
            v-if="
                props.cardXNodeXWidgetData?.widget?.name ===
                'radio-boolean-widget'
            "
            :id="`${props.graphSlug}-${props.nodeAlias}-input`"
        >
            <div>
                <RadioButton
                    v-model="props.value.interchange_value"
                    v-bind:value="true"
                    inputId="`${props.graphSlug}-${props.nodeAlias}-true`"
                />
                <label
                    v-text="props.cardXNodeXWidgetData.node.config.trueLabel"
                    for="`${props.graphSlug}-${props.nodeAlias}-true`"
                ></label>
            </div>
            <div>
                <RadioButton
                    v-model="props.value.interchange_value"
                    v-bind:value="false"
                    inputId="`${props.graphSlug}-${props.nodeAlias}-false`"
                />
                <label
                    v-text="props.cardXNodeXWidgetData.node.config.falseLabel"
                    for="`${props.graphSlug}-${props.nodeAlias}-false`"
                ></label>
            </div>
        </RadioButtonGroup>
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
