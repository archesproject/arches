<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";

const { displayedList, editable } = defineProps(["displayedList", "editable"]);

const editing = ref(false);
const disabled = computed(() => {
    return !editable.value || !editing.value;
});

const staticLabel = "Static: list does not change";
const dynamicLabel =
    "Dynamic: list is defined by a query that may change list items";
</script>

<template>
    <div class="characteristics">
        <h4>Characteristics</h4>
        <div class="characteristic">
            <h5>Name</h5>
            <!-- TODO wire up with v-model and factor out into component for use with URI -->
            <input
                :disabled="disabled"
                :value="displayedList.value.name"
                :style="{ width: displayedList.value.name.length + 'rem' }"
            />
            <span v-if="editable && !editing" class="edit-controls">
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
                ></i>
            </span>
            <span v-if="editable && editing" class="edit-controls">
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
                ></i>
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
                ></i>
            </span>
        </div>
        <div class="characteristic">
            <h5>Type</h5>
            <input
                :disabled="disabled"
                :value="
                    displayedList.value.dynamic ? dynamicLabel : staticLabel
                "
                :style="{
                    width: displayedList.value.dynamic
                        ? dynamicLabel.length + 'rem'
                        : staticLabel.length + 'rem',
                }"
            />
        </div>
        <div class="characteristic">
            <h5>List used by these nodes</h5>
        </div>
    </div>
</template>

<style scoped>
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
