<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";
import { useToast } from "primevue/usetoast";

import {
    postItemToServer,
    postListToServer,
} from "@/components/ControlledListManager/api.ts";
import type {
    ControlledList,
    ControlledListItem,
    Selectable,
} from "@/types/ControlledListManager";

const props: {
    item: Selectable;
    editable: boolean;
    field: "name" | "dynamic" | "uri";
    label: string;
} = defineProps(["item", "editable", "field", "label"]);

const editing = ref(false);
const disabled = computed(() => {
    return !props.editable || !editing.value;
});

const dirtyFormValue = ref("");

const inputValue = computed({
    get() {
        if (props.field === "uri") {
            return (props.item as ControlledListItem)[props.field];
        } else {
            return (props.item as ControlledList)[props.field];
        }
    },
    set(newVal: string) {
        dirtyFormValue.value = newVal;
    },
});

const width = computed(() => {
    if (props.field === "uri") {
        return "100%";
    }
    return '12rem'; // todo: change in next iteration
});

const toast = useToast();
const { $gettext } = useGettext();

const onSave = () => {
    editing.value = false;

    const field = props.field;
    if (field === "uri") {
        // eslint-disable-next-line vue/no-mutating-props
        (props.item as ControlledListItem)[field] = dirtyFormValue.value;
    }
    if (field === 'name') {
        // eslint-disable-next-line vue/no-mutating-props
        (props.item as ControlledList)[field] = dirtyFormValue.value;
    }

    const isList = Object.hasOwn(props.item, "items");
    const saveFn = isList ? postListToServer : postItemToServer;
    saveFn(props.item, toast, $gettext);
};
const onCancel = () => {
    editing.value = false;

    let originalValue;
    if (props.field === "uri") {
        originalValue = (props.item as ControlledListItem)[props.field];
    } else {
        originalValue = (props.item as ControlledList)[props.field];
    }

    dirtyFormValue.value = originalValue;
};
</script>

<template>
    <div class="characteristic">
        <h4>{{ props.label }}</h4>
        <InputText
            v-model="inputValue"
            type="text"
            class="control"
            :disabled="disabled"
            :style="{ width: width }"
        />
        <span
            v-if="props.editable && !editing"
            class="edit-controls"
        >
            <i
                role="button"
                tabindex="0"
                class="fa fa-pencil"
                :aria-label="arches.translations.edit"
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
                :aria-label="arches.translations.saveEdit"
                @click="onSave"
                @keyup.enter="onSave"
            />
            <i
                role="button"
                tabindex="0"
                class="fa fa-times"
                :aria-label="arches.translations.cancelEdit"
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
}
</style>
