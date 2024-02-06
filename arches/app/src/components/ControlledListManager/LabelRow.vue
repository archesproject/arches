<script setup lang="ts">
import arches from "arches";

import type { Label } from "@/types/ControlledListManager.d";

const props: { label: Label } = defineProps(["label"]);
</script>

<template>
    <div class="label-container">
        <span class="label">{{ props.label.value }}</span>
        <div class="label-end">
            <span class="controls">
                <button>{{ arches.translations.delete }}</button>
                <button>{{ arches.translations.edit }}</button>
            </span>
            <span class="label language">{{ props.label.language }}</span>
        </div>
    </div>
</template>

<style scoped>
.label-container {
    display: flex;
    justify-content: space-between;
    background: #f3fbfd;
    border: 1px solid lightgray;
}
span {
    margin: 1rem;
}
.label {
    color: black;
}
.controls {
    display: inline-flex;
    justify-content: space-between;
    min-width: 7rem;
}
button {
    color: var(--blue-500);
    font-size: smaller;
    background: none;
    border: none;
}
.label.language {
    width: 4rem;
    height: 2rem;
    border-radius: 1px;
    background: var(--gray-200);
}
</style>
