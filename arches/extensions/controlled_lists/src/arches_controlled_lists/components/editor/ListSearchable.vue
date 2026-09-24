<script setup lang="ts">
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import ToggleSwitch from "primevue/toggleswitch";
import { useToast } from "primevue/usetoast";

import { patchList } from "@/arches_controlled_lists/api.ts";
import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    displayedRowKey,
} from "@/arches_controlled_lists/constants.ts";

import type { Ref } from "vue";
import type { ControlledList } from "@/arches_controlled_lists/types";

const { displayedRow: list } = inject(displayedRowKey) as unknown as {
    displayedRow: Ref<ControlledList>;
};

const formValue = ref(false);
// Update fields
const field = "searchable";

const inputValue = computed({
    get() {
        return list.value.searchable;
    },
    set(newVal: boolean) {
        formValue.value = newVal;
    },
});

const toast = useToast();
const { $gettext } = useGettext();

const save = async () => {
    const originalValue = list.value.searchable;
    list.value.searchable = formValue.value;
    try {
        await patchList(list.value!, field);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Save failed"),
            detail: error instanceof Error ? error.message : undefined,
        });
        list.value.searchable = originalValue;
    }
};
</script>

<template>
    <div class="characteristic">
        <div class="value-editor-title">
            <label for="searchableSwitch">
                {{ $gettext("Searchable?") }}
            </label>
        </div>
        <div class="searchable-switch">
            <ToggleSwitch
                v-model="inputValue"
                input-id="searchableSwitch"
                @change="save"
            />
        </div>
    </div>
</template>

<style scoped>
.characteristic {
    margin: 1rem 1rem 2.5rem 1rem;
}

.value-editor-title {
    display: flex;
    gap: 1rem;
}

.value-editor-title label {
    font-size: 1.66rem;
    margin: 0;
    padding: 0.5rem 0 0 0;
    font-weight: 400;
}

.searchable-switch {
    display: inline-flex;
    gap: 1rem;
    padding: 0.5rem 0 0 0;
    align-items: center;
}
</style>
