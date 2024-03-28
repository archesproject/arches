<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { postListToServer } from "@/components/ControlledListManager/api.ts";
import { displayedRowKey } from "@/components/ControlledListManager/const.ts";

const props: {
    editable: boolean;
    field: "name" | "dynamic";
    label: string;
} = defineProps(["editable", "field", "label"]);
const { displayedRow } = inject(displayedRowKey);

const editing = ref(false);
const disabled = computed(() => {
    return !props.editable || !editing.value;
});

const formValue = ref("");

const inputValue = computed({
    get() {
        return displayedRow.value[props.field];
    },
    set(newVal: string) {
        formValue.value = newVal;
    },
});

const toast = useToast();
const { $gettext } = useGettext();

const onSave = async () => {
    editing.value = false;
    const originalValue = displayedRow.value[props.field];
    displayedRow.value[props.field] = formValue.value;
    const success = await postListToServer(displayedRow.value, toast, $gettext);
    if (!success) {
        displayedRow.value[props.field] = originalValue;
    }
};

const onCancel = () => {
    editing.value = false;
    formValue.value = displayedRow.value[props.field];
};
</script>

<template>
    <div class="characteristic">
        <h4>{{ props.label }}</h4>
        <InputText
            v-model="inputValue"
            type="text"
            :disabled="disabled"
        />
        <span
            v-if="props.editable && !editing"
            class="edit-controls"
        >
            <i
                role="button"
                tabindex="0"
                class="fa fa-pencil"
                :aria-label="$gettext('Edit')"
                @click="editing = true"
                @keyup.enter="editing = true"
            />
        </span>
        <span
            v-if="props.editable && editing"
            class="edit-controls"
        >
            <i
                role="button"
                tabindex="0"
                class="fa fa-check"
                :aria-label="$gettext('Save edit')"
                @click="onSave"
                @keyup.enter="onSave"
            />
            <i
                role="button"
                tabindex="0"
                class="fa fa-times"
                :aria-label="$gettext('Cancel edit')"
                @click="onCancel"
                @keyup.enter="onCancel"
            />
        </span>
    </div>
</template>

<style scoped>
h4,
input {
    font-size: 1.25rem;
}

.characteristic {
    margin: 1rem 1rem 2rem 1rem;
}

.characteristic input {
    text-align: center;
    border-width: 2px;
    height: 3rem;
    width: 12rem;
}

.characteristic input[disabled] {
    background: var(--gray-400);
}

.edit-controls {
    margin-left: 1rem;
    display: inline-flex;
    justify-content: space-between;
    width: 4rem;
}

.edit-controls i {
    font-size: medium;
    padding: 4px;
}
</style>
