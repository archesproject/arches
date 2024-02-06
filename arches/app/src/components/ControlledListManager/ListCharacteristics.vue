<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import InputText from "primevue/inputtext";

import { postDisplayedListToServer } from "@/components/ControlledListManager/api.ts";

import type { ControlledList } from "@/types/ControlledListManager.d";

const props: {
    displayedList: ControlledList;
    editable: boolean;
} = defineProps([
    "displayedList",
    "editable",
]);

const nameValue = ref(props.displayedList.name);
const editing = ref(false);
const disabled = computed(() => {
    return !props.editable || !editing.value;
});

const { $gettext } = useGettext();
const staticLabel = $gettext("Static: list does not change");
const dynamicLabel =
    $gettext("Dynamic: list is defined by a query that may change list items");
</script>

<template>
    <div class="characteristics">
        <h3>{{ $gettext("Characteristics") }}</h3>
        <div class="characteristic">
            <h4>{{ $gettext("Name") }}</h4>
            <InputText
                v-model="nameValue"
                type="text"
                class="control"
                :disabled="disabled"
                :style="{ width: Math.max(nameValue.length + 2, 4) + 'rem' }"
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
                    @click="
                        () => {
                            editing = true;
                        }
                    "
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
                    @click="
                        () => {
                            editing = false;
                            // eslint-disable-next-line vue/no-mutating-props
                            props.displayedList.name = nameValue;
                            postDisplayedListToServer(props.displayedList, toast, $gettext);
                        }
                    "
                />
                <i
                    role="button"
                    tabindex="0"
                    class="fa fa-times"
                    :aria-label="arches.translations.cancelEdit"
                    @click="
                        () => {
                            editing = false;
                            nameValue = props.displayedList.name;
                        }
                    "
                />
            </span>
        </div>
        <div class="characteristic">
            <h4>{{ $gettext("Type") }}</h4>
            <input
                disabled
                :value="
                    props.displayedList.dynamic ? dynamicLabel : staticLabel
                "
                :style="{
                    width: props.displayedList.dynamic
                        ? dynamicLabel.length - 20 + 'rem'
                        : staticLabel.length - 10 + 'rem',
                }"
            >
        </div>
        <div class="characteristic">
            <h4>{{ $gettext("List used by these nodes") }}</h4>
        </div>
    </div>
</template>

<style scoped>
h3 {
    font-size: 1.5rem;
}
h4,
input {
    font-size: 1.25rem;
}
.characteristics {
    padding-top: 0.125rem;
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
