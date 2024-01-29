<script setup>
import arches from "arches";
import Button from "primevue/button";

const { editingListId, openListEditor } = defineProps([
    "editingListId",
    "openListEditor",
]);
</script>

<template>
    <Button @click="() => openListEditor('')">{{
        arches.translations.return
    }}</Button>
</template>

<style scoped></style>
