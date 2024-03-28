<script setup lang="ts">
import Toast from "primevue/toast";

import ControlledListEditor from "@/components/ControlledListManager/ControlledListEditor.vue";
</script>

<template>
    <!-- Subtract size of arches toolbars -->
    <div style="width: calc(100vw - 50px); height: calc(100vh - 50px)">
        <div style="height: 100%">
            <ControlledListEditor />
        </div>
    </div>
    <Toast />
</template>

<!-- Not scoped: workaround for lack of font-family in <body> -->
<style>
div {
    font-family: "Open Sans";
}
</style>
