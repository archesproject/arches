<script setup lang="ts">
import { useGettext } from 'vue3-gettext';
const { $gettext } = useGettext();

console.log($gettext('Hello from the <script> tag!'));
</script>


<template>
    <h1 class="header">
        {{ $gettext("Hello from the template!") }}
    </h1>
</template>


<style scoped>
.header {
    color: red;
}
</style>