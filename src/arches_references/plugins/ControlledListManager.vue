<script setup lang="ts">
import Toast from "primevue/toast";

import ControlledListsMain from "@/arches_references/components/ControlledListsMain.vue";
</script>

<template>
    <!-- Subtract size of arches toolbars -->
    <div style="width: calc(100vw - 50px); height: calc(100vh - 50px)">
        <div style="height: 100%">
            <ControlledListsMain />
        </div>
    </div>
    <Toast />
</template>

<style scoped>
:deep(h1, h5, h6) {
    font-weight: 600;
}

:deep(h2, h3) {
    font-weight: 600;
    font-size: 1.6rem;
}

:deep(h4) {
    font-weight: 600;
    font-size: 1.33rem;
}
</style>
