<script setup lang="ts">
import arches from "arches";

import Button from "primevue/button";
import InputText from "primevue/inputtext";
import SplitButton from "primevue/splitbutton";

const buttonGreen = "#10b981";
const buttonPink = "#ed7979";

const {
    addLabel,
    createItem,
    deleteItems,
    deleteLabel,
    deleteLabelPlural,
    items,
    numberToDelete,
} = defineProps([
    "addLabel",
    "createItem",
    "deleteItems",
    "deleteLabel",
    "deleteLabelPlural",
    "items",
    "numberToDelete",
]);

const searchValue = defineModel({ type: String });

const clearSearch = () => {
    searchValue.value = "";
};
</script>

<template>
    <div class="controls">
        <span class="flex p-input-icon-right">
            <InputText
                type="text"
                class="control"
                :placeholder="arches.translations.find"
                v-model="searchValue"
            />
            <i
                v-if="searchValue"
                class="fa fa-times"
                role="button"
                tabindex="0"
                @click="clearSearch"
                @keydown="clearSearch"
                :aria-label="arches.translations.clear"
            ></i>
            <i
                v-else
                class="fa fa-search"
                :aria-label="arches.translations.search"
            ></i>
        </span>
        <div class="flex" style="flex: 0.8; flex-wrap: wrap">
            <SplitButton
                class="button"
                :label="addLabel"
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
                @click="createItem"
            ></SplitButton>
            <!-- We might want an are you sure? modal -->
            <Button
                class="button delete"
                :label="numberToDelete > 1 ? deleteLabelPlural : deleteLabel"
                raised
                :disabled="numberToDelete === 0"
                @click="deleteItems"
            ></Button>
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
    margin-top: -0.75rem;
    margin-right: 2rem;
}
.p-inputtext {
    flex: 0.95;
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
