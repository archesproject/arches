<script setup>
import arches from "arches";
import Button from "primevue/button";

import Characteristics from "./Characteristics.vue";
import Header from "./Header.vue";

const { displayedList, editing, setEditing } = defineProps([
    "displayedList",
    "editing",
    "setEditing",
]);
</script>

<template>
    <Header :displayedList="displayedList" :isItemEditor="true"></Header>
    <div class="list-editor-container">
        <Characteristics :displayedList="displayedList" />
        <Button @click="setEditing(false)">{{
            arches.translations.return
        }}</Button>
    </div>
</template>

<style scoped></style>
