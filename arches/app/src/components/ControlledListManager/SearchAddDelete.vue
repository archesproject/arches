<script setup lang="ts">
import arches from "arches";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import InputText from "primevue/inputtext";
import SplitButton from "primevue/splitbutton";

import type { Ref } from "@/types/Ref";

const buttonGreen = "#10b981";
const buttonPink = "#ed7979";

const props: {
    createAction: () => Promise<void>;
    delAction: () => Promise<void>;
    numberToDelete: number;
} = defineProps([
    "createAction",
    "delAction",
    "numberToDelete",
]);

const searchValue: Ref<string> = defineModel({ required: true });

const { $gettext } = useGettext();
const ADD_NEW_LIST = $gettext("Add New List");
const DELETE_LIST = $gettext("Delete List");
const DELETE_LISTS = $gettext("Delete Lists");

const clearSearch = () => {
    searchValue.value = "";
};
</script>

<template>
    <div class="controls">
        <span class="flex p-input-icon-right">
            <InputText
                v-model="searchValue"
                type="text"
                class="control"
                :placeholder="$gettext('Find')"
            />
            <i
                v-if="searchValue"
                class="fa fa-times"
                role="button"
                tabindex="0"
                :aria-label="$gettext('Clear')"
                @click="clearSearch"
                @keydown="clearSearch"
            />
            <i
                v-else
                class="fa fa-search"
                :aria-label="$gettext('Search')"
            />
        </span>
        <div
            class="flex"
            style="flex-wrap: wrap"
        >
            <SplitButton
                class="button"
                :label="ADD_NEW_LIST"
                raised
                style="font-size: inherit"
                :pt="{
                    button: {
                        root: {
                            style: {
                                background: buttonGreen,
                                border: `1px solid ${buttonGreen}`,
                            },
                        },
                    },
                    menubutton: {
                        root: {
                            style: {
                                background: buttonGreen,
                                border: `1px solid ${buttonGreen}`,
                            },
                        },
                    },
                }"
                @click="props.createAction"
            />
            <!-- We might want an are you sure? modal -->
            <Button
                class="button delete"
                :label="props.numberToDelete > 1 ? DELETE_LISTS : DELETE_LIST"
                raised
                :disabled="props.numberToDelete === 0"
                @click="props.delAction"
            />
        </div>
    </div>
</template>

<style scoped>
.controls {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    background: #f3fbfd;
}
.controls i {
    align-self: center;
}
.p-inputtext {
    flex: 1;
    margin: 0.5rem;
}
.button {
    height: 4rem;
    margin: 0.5rem;
    flex: 0.5;
    justify-content: center;
    font-weight: 600;
    color: white;
    text-wrap: nowrap;
}
.button.delete {
    background: v-bind(buttonPink);
    border: 1px solid v-bind(buttonPink);
}
</style>
