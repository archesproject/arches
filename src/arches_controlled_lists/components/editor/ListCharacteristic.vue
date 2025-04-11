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
const { displayedRow: list } = inject(displayedRowKey) as unknown as {
    displayedRow: Ref<ControlledList>;
};
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
    list.value.name = formValue.value.trim();
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
        <h4>{{ props.label }}</h4>
        <!-- TODO https://github.com/archesproject/arches/issues/10847 -->
        <span
            v-if="!props.editable"
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
</template>

<style scoped>
input {
    font-size: 1.2rem;
}

.characteristic {
    margin: 1rem 1rem 2rem 1rem;
}

.characteristic input {
    text-align: center;
    border-width: 2px;
    height: 3rem;
    width: 30rem;
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
    font-size: medium;
    padding: 0.5rem;
}
</style>
