<script setup>
import arches from "arches";
import Cookies from "js-cookie";
import { ref } from "vue";

import Button from "primevue/button";
import InputText from "primevue/inputtext";
import SplitButton from "primevue/splitbutton";
import { useToast } from "primevue/usetoast";

import ControlledListsAll from "./ControlledListsAll.vue";
import Spinner from "../Spinner.vue";

const buttonGreen = "#10b981";
const buttonPink = "#ed7979";
const toast = useToast();

const { displayedList, languageMap } = defineProps([
    "displayedList",
    "languageMap",
]);
const selectedLists = ref([]);
const searchValue = ref("");
const queryMutator = ref(0);

const clearSearch = () => {
    searchValue.value = "";
};

const createList = async () => {
    try {
        const response = await fetch(arches.urls.controlled_lists, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        });
        if (response.ok) {
            queryMutator.value += 1;
        } else {
            throw new Error();
        }
    } catch {
        toast.add({
            severity: "error",
            summary: "List creation failed",
            life: 3000,
        });
    }
};

const deleteLists = async () => {
    if (!selectedLists.value.length) {
        return;
    }
    const promises = selectedLists.value.map((list) =>
        fetch(arches.urls.controlled_list(list.id), {
            method: "DELETE",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        })
    );

    try {
        const responses = await Promise.all(promises);
        if (responses.some((resp) => resp.ok)) {
            if (selectedLists.value.includes(displayedList.value)) {
                displayedList.value = null;
            }
            selectedLists.value = [];

            queryMutator.value += 1;
        }
        if (responses.some((resp) => !resp.ok)) {
            throw new Error();
        }
    } catch {
        toast.add({
            severity: "error",
            summary: "One or more lists failed to delete.",
            life: 3000,
        });
    }
};
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
                @click="createList"
            ></SplitButton>
            <!-- We might want an are you sure? modal -->
            <Button
                class="button delete"
                :label="
                    selectedLists.length > 1 ? 'Delete Lists' : 'Delete List'
                "
                raised
                :disabled="!selectedLists.length"
                @click="deleteLists"
            ></Button>
        </div>
    </div>

    <Suspense>
        <ControlledListsAll
            :displayedList="displayedList"
            :selectedLists="selectedLists"
            :searchValue="searchValue"
            :languageMap="languageMap"
            :key="queryMutator"
        />
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
