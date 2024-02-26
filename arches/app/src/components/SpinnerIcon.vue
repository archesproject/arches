<script setup lang="ts">
import { useGettext } from "vue3-gettext";

const { $gettext } = useGettext();
</script>

<template>
    <div id="spinner-container">
        <i
            class="fa fa-spin fa-spinner"
            :aria-label="$gettext('Loading data')"
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
