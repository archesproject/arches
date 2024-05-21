<script setup lang="ts">
import { useGettext } from "vue3-gettext";

const { $gettext } = useGettext();
</script>

<template>
    <div class="controlled-list-splash">
        <div
            aria-hidden="true"
            class="img-lg img-circle controlled-list-splash-img-container"
        >
            <i class="fa fa-list" />
        </div>

        <div class="controlled-list-splash-title">
            {{ $gettext("Welcome to Arches' Controlled List Manager") }}
        </div>

        <div class="controlled-list-splash-description">
            {{ $gettext("Select a list from the sidebar.") }}
        </div>
    </div>
</template>

<style scoped>
.controlled-list-splash {
    text-align: center;
    margin: 48px 45px 20px 45px;
    border: 1px solid #ddd;
    padding: 40px 30px;
    background: #f6f6f6;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.controlled-list-splash-title {
    color: #666;
    font-size: 2.8rem;
    margin-bottom: 30px;
    margin-top: 25px;
}

i {
    color: steelblue;
    font-size: xx-large;
    display: flex;
    height: 100%;
    justify-content: center;
    align-items: center;
}

.controlled-list-splash-img-container {
    padding: 20px;
    background: #fff;
    border: 1px solid steelblue;
    display: inline-block;
}

.controlled-list-splash-description {
    font-size: 1.5rem;
    color: #999;
    font-weight: 500;
}
</style>
