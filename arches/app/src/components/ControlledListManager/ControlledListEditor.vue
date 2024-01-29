<script setup>
import arches from "arches";
import Button from "primevue/button";

import Characteristics from "./Characteristics.vue";

const { displayedList, editing, setEditing } = defineProps([
    "displayedList",
    "editing",
    "setEditing",
]);
</script>

<template>
    <Characteristics :displayedList="displayedList" />
    <Button @click="setEditing(false)">{{ arches.translations.return }}</Button>
</template>

<style scoped></style>
