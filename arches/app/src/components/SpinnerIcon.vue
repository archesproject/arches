<script setup lang="ts">
import arches from "arches";
</script>

<template>
    <div id="spinner-container">
        <i
            class="fa fa-spin fa-spinner"
            :aria-label="arches.translations.loadingData"
        />
    </div>
</template>

<style scoped>
#spinner-container {
    font-size: 36px;
    position: relative;
    width: 100%;
    height: 100%;
}
.fa-spinner {
    position: relative;
    top: 50%;
    left: 45%;
}
</style>
