<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import { patchItem } from "@/arches_controlled_lists/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    itemKey,
} from "@/arches_controlled_lists/constants.ts";
import { vFocus } from "@/arches_controlled_lists/utils.ts";

import type { Ref } from "vue";
import type { ControlledListItem } from "@/arches_controlled_lists/types";

const item = inject(itemKey) as Ref<ControlledListItem>;

const isEditing = ref(false);
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
    isEditing.value = false;
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

const cancel = () => {
    isEditing.value = false;
    formValue.value = item.value.uri;
};

defineExpose({ isEditing });
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
                :disabled="!isEditing"
                :aria-label="$gettext('Enter a URI')"
                :placeholder="$gettext('Enter a URI')"
                @keyup.enter="save"
            />
            <span
                v-if="!isEditing"
                class="edit-controls"
            >
                <i
                    role="button"
                    tabindex="0"
                    class="fa fa-pencil"
                    :aria-label="$gettext('Edit')"
                    @click="isEditing = true"
                    @keyup.enter="isEditing = true"
                />
            </span>
            <span
                v-if="isEditing"
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
    margin: 1rem 1rem 3rem 1rem;
    display: flex;
    flex-direction: column;
    width: 100%;
}

h4 {
    margin-top: 0;
}

p {
    font-weight: normal;
    margin-top: 0;
    font-size: 1.2rem;
}

input {
    font-size: 1.2rem;
}

.characteristic {
    margin: 1rem;
    display: flex;
    align-items: center;
}

.characteristic input {
    text-align: center;
    height: 3rem;
    width: 100%;
}

.characteristic input[disabled] {
    text-align: left;
}

.edit-controls {
    margin-left: 1rem;
    display: inline-flex;
    justify-content: space-between;
    width: 4rem;
}

.edit-controls i {
    font-size: var(--p-icon-size);
    padding: 0.5rem;
}
</style>
