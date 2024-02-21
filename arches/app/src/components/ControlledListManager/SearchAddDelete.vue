<script setup lang="ts">
import arches from "arches";

import Button from "primevue/button";
import InputText from "primevue/inputtext";
import SplitButton from "primevue/splitbutton";

const buttonGreen = "#10b981";
const buttonPink = "#ed7979";

const props: {
    addLabel: string;
    createAction: () => Promise<void>;
    delAction: () => Promise<void>;
    delLabel: string;
    delLabelPlural: string;
    numberToDelete: number;
} = defineProps([
    "addLabel",
    "createAction",
    "delAction",
    "delLabel",
    "delLabelPlural",
    "numberToDelete",
]);

const searchValue = defineModel<string>({ required: true });

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
                :placeholder="arches.translations.find"
            />
            <i
                v-if="searchValue"
                class="fa fa-times"
                role="button"
                tabindex="0"
                :aria-label="arches.translations.clear"
                @click="clearSearch"
                @keydown="clearSearch"
            />
            <i
                v-else
                class="fa fa-search"
                :aria-label="arches.translations.search"
            />
        </span>
        <div
            class="flex"
            style="flex-wrap: wrap"
        >
            <SplitButton
                class="button"
                :label="props.addLabel"
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
                :label="props.numberToDelete > 1 ? props.delLabelPlural : props.delLabel"
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
    margin-top: -0.75rem;
    margin-right: 2rem;
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
