<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { patchList } from "@/arches_controlled_lists/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    displayedRowKey,
    isEditingKey,
} from "@/arches_controlled_lists/constants.ts";
import { vFocus } from "@/arches_controlled_lists/utils.ts";

import type { Ref } from "vue";
import type {
    ControlledList,
    IsEditingRefAndSetter,
} from "@/arches_controlled_lists/types";

const props = defineProps<{
    editable: boolean;
    label: string;
}>();
const { displayedRow: list } = inject<{ displayedRow: Ref<ControlledList> }>(
    displayedRowKey,
)!;
const { isEditing, setIsEditing } = inject(
    isEditingKey,
) as IsEditingRefAndSetter;

const disabled = computed(() => {
    return !props.editable || !isEditing.value;
});

const formValue = ref("");
// Update fields
const field = "name";

const inputValue = computed({
    get() {
        return list.value.name;
    },
    set(newVal: string) {
        formValue.value = newVal;
    },
});

const toast = useToast();
const { $gettext } = useGettext();

const save = async () => {
    isEditing.value = false;
    const originalValue = list.value.name;
    list.value.name = formValue.value.trim() || originalValue;
    try {
        await patchList(list.value!, field);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        list.value.name = originalValue;
    }
};

const cancel = () => {
    isEditing.value = false;
    formValue.value = list.value.name;
};
</script>

<template>
    <div class="characteristic">
        <div>
            <div class="value-editor-title">
                <h4>{{ props.label }}</h4>
            </div>

            <!-- TODO https://github.com/archesproject/arches-controlled-lists/issues/7 -->
            <span
                v-if="!props.editable"
                class="value-label"
                style="font-size: small"
            >
                {{ $gettext("False") }}
            </span>

            <InputText
                v-else
                v-model="inputValue"
                v-focus
                type="text"
                :disabled="disabled"
                @keyup.enter="save"
            />

            <span
                v-if="props.editable && !isEditing"
                class="edit-controls"
            >
                <i
                    role="button"
                    tabindex="0"
                    class="fa fa-pencil"
                    :aria-label="$gettext('Edit')"
                    @click="setIsEditing(true)"
                    @keyup.enter="setIsEditing(true)"
                ></i>
            </span>
            <span
                v-if="props.editable && isEditing"
                class="edit-controls"
            >
                <i
                    role="button"
                    tabindex="0"
                    class="fa fa-check"
                    :aria-label="$gettext('Save edit')"
                    @click="save"
                    @keyup.enter="save"
                ></i>
                <i
                    role="button"
                    tabindex="0"
                    class="fa fa-undo"
                    :aria-label="$gettext('Cancel edit')"
                    @click="cancel"
                    @keyup.enter="cancel"
                ></i>
            </span>
        </div>
    </div>
</template>

<style scoped>
input {
    font-size: 1.2rem;
    border-radius: 2px;
}

.characteristic {
    margin: 1rem 1rem 2.5rem 1rem;
}

.value-editor-title {
    display: flex;
    gap: 1rem;
}

.value-editor-title h4 {
    font-size: 1.66rem;
    margin: 0;
    padding: 0.5rem 0 0.5rem 0;
    font-weight: 400;
}

.value-label {
    color: var(--p-text-muted-color);
}

.characteristic input {
    border-width: 2px;
    height: 3rem;
    width: 30rem;
}

.characteristic input[disabled] {
    text-align: left;
}

.edit-controls {
    margin-inline-start: 1rem;
    display: inline-flex;
    justify-content: space-between;
    width: 4rem;
}

.edit-controls i {
    font-size: medium;
    align-self: center;
    padding: 0.5rem;
    border-radius: 50%;
}

.edit-controls i.fa-check:hover {
    background: var(--p-button-primary-hover-background);
    color: var(--p-button-primary-hover-color);
}

.edit-controls i.fa-undo:hover {
    background: var(--p-amber-300);
    color: var(--p-button-primary-hover-color);
}
</style>
