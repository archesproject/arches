<script setup>
import arches from "arches";

import Button from "primevue/button";
import InputText from "primevue/inputtext";
import SplitButton from "primevue/splitbutton";

import ControlledListsAll from "./ControlledListsAll.vue";
import Spinner from "./Spinner.vue";

const buttonGreen = "#10b981";
const buttonPink = "#ed7979";

const { selectedList } = defineProps(["selectedList"]);
</script>

<template>
    <div class="header">
        <h4>Controlled Lists</h4>
    </div>

    <div class="controls">
        <span class="flex p-input-icon-right">
            <InputText
                type="text"
                class="control"
                :placeholder="arches.translations.find"
            />
            <i
                class="fa fa-search"
                :aria-label="arches.translations.search"
            ></i>
        </span>
        <div class="flex" style="flex: 0.8; flex-wrap: wrap">
            <SplitButton
                class="button"
                label="Create New List"
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
            ></SplitButton>
            <Button class="button delete" label="Delete List" raised></Button>
        </div>
    </div>

    <Suspense>
        <ControlledListsAll :selectedList="selectedList" />
        <template #fallback>
            <Spinner />
        </template>
    </Suspense>
</template>

<style scoped>
.header {
    background: #f4f4f4;
    display: flex;
    align-items: center;
}
h4 {
    margin: 1rem;
}
i {
    margin-top: -0.75rem;
    margin-right: 2rem;
}
.controls {
    display: flex;
    flex-direction: column;
    padding: 1rem;
    background: #f3fbfd;
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
