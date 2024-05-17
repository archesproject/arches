<script setup lang="ts">
import ConfirmDialog from "primevue/confirmdialog";
import Toast from "primevue/toast";

import ControlledListsMain from "@/controlled-lists/components/ControlledListsMain.vue";
</script>

<template>
    <!-- Subtract size of arches toolbars -->
    <div style="width: calc(100vw - 50px); height: calc(100vh - 50px)">
        <div style="height: 100%">
            <ControlledListsMain />
        </div>
    </div>
    <ConfirmDialog :draggable="false" />
    <Toast />
    <RouterView />
</template>

<!-- Not scoped: workaround for lack of font-family in <body> -->
<style>
div {
    font-family: "Open Sans";
}
</style>
