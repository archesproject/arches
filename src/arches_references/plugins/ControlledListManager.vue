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
