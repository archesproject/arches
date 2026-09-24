<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { patchItem } from "@/arches_controlled_lists/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    isEditingKey,
    itemKey,
} from "@/arches_controlled_lists/constants.ts";
import { vFocus } from "@/arches_controlled_lists/utils.ts";

import type { Ref } from "vue";
import type {
    ControlledListItem,
    IsEditingRefAndSetter,
} from "@/arches_controlled_lists/types";

const item = inject(itemKey) as Ref<ControlledListItem>;
const { isEditing, setIsEditing } = inject(
    isEditingKey,
) as IsEditingRefAndSetter;

const isEditingUri = ref(false);
const formValue = ref("");

const inputValue = computed({
    get() {
        return item.value.uri;
    },
    set(newVal: string) {
        formValue.value = newVal;
    },
});

const toast = useToast();
const { $gettext } = useGettext();
const uri = "uri";

const save = async () => {
    setIsEditing(false);
    isEditingUri.value = false;
    const originalValue = item.value.uri;
    item.value.uri = formValue.value;

    try {
        await patchItem(item.value, uri);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        item.value.uri = originalValue;
    }
};

function cancel() {
    setIsEditing(false);
    isEditingUri.value = false;
    formValue.value = item.value.uri;
}

function tryEdit() {
    if (!isEditing.value) {
        isEditing.value = true;
        isEditingUri.value = true;
    }
}
</script>

<template>
    <div class="uri-container">
        <h4>{{ $gettext("List Item URI") }}</h4>
        <p>
            {{
                $gettext(
                    "Optionally, provide a URI for your list item. Useful if your list item is formally defined in a thesaurus or authority document.",
                )
            }}
        </p>
        <div class="characteristic">
            <InputText
                v-model="inputValue"
                v-focus
                type="text"
                :disabled="!isEditing || !isEditingUri"
                :aria-label="$gettext('Enter a URI')"
                :placeholder="$gettext('Enter a URI')"
                @keyup.enter="save"
            />
            <span
                v-if="!isEditingUri"
                class="edit-controls"
            >
                <i
                    role="button"
                    tabindex="0"
                    class="fa fa-pencil"
                    :aria-label="$gettext('Edit')"
                    @click="tryEdit"
                    @keyup.enter="tryEdit"
                />
            </span>
            <span
                v-if="isEditingUri"
                class="edit-controls"
            >
                <i
                    role="button"
                    tabindex="0"
                    class="fa fa-check"
                    :aria-label="$gettext('Save edit')"
                    @click="save"
                    @keyup.enter="save"
                />
                <i
                    role="button"
                    tabindex="0"
                    class="fa fa-undo"
                    :aria-label="$gettext('Cancel edit')"
                    @click="cancel"
                    @keyup.enter="cancel"
                />
            </span>
        </div>
    </div>
</template>

<style scoped>
.uri-container {
    margin: 1rem 1rem 4rem 2rem;
    display: flex;
    flex-direction: column;
    width: 90%;
}

.uri-container h4 {
    font-size: 1.66rem;
    margin: 0;
    padding: 0.5rem 0 0 0;
    font-weight: 400;
}

.uri-container p {
    margin: 0;
    padding: 0.25rem 1rem 0 0;
    color: var(--p-text-muted-color);
}

input {
    font-size: 1.2rem;
    border-radius: 2px;
}

.characteristic {
    margin: 0.5rem 0 0 0;
    display: flex;
}

.characteristic input {
    height: 3rem;
    padding: 1.5rem 0.5rem;
    width: 100%;
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
    font-size: var(--p-icon-size);
    align-self: center;
}

:deep(i[role="button"]) {
    height: var(--p-button-icon-only-width);
    width: var(--p-button-icon-only-width);
    border-radius: 50%;
    border: 1px solid var(--p-button-secondary-border-color);
    background: var(--p-button-secondary-background);
    padding: 0.67rem;
}

:deep(i[role="button"]:hover) {
    background: var(--p-button-primary-hover-background);
    color: var(--p-button-primary-hover-color);
}

:deep(i.fa-undo[role="button"]:hover) {
    background: var(--p-amber-300);
    color: var(--p-button-primary-hover-color);
}
</style>
