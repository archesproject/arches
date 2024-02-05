<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import type { ControlledList } from "@/types/ControlledListManager.d";

const {
    displayedList,
    editable,
}: { displayedList: ControlledList; editable: boolean } = defineProps([
    "displayedList",
    "editable",
]);

const editing = ref(false);
const disabled = computed(() => {
    return !editable || !editing.value;
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
            <h4>Name</h4>
            <!-- TODO wire up with v-model and factor out into component for use with URI -->
            <input
                :disabled="disabled"
                :value="displayedList.name"
                :style="{ width: displayedList.name.length + 2 + 'rem' }"
            >
            <span
                v-if="editable && !editing"
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
                v-if="editable && editing"
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
                        }
                    "
                />
            </span>
        </div>
        <div class="characteristic">
            <h4>Type</h4>
            <input
                :disabled="disabled"
                :value="
                    displayedList.dynamic ? dynamicLabel : staticLabel
                "
                :style="{
                    width: displayedList.dynamic
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
    background: var(--gray-400);
    border-width: 2px;
    height: 3rem;
}
.edit-controls {
    margin-left: 1rem;
}
.edit-controls i {
    border: 2px solid;
}
</style>
