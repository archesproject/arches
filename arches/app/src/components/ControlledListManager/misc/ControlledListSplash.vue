<script setup lang="ts">
import { useGettext } from "vue3-gettext";

const { $gettext } = useGettext();
</script>

<template>
    <div class="controlled-list-splash">
        <div
            aria-hidden="true"
            class="splash-large splash-circle controlled-list-splash-img-container"
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
.splash-large {
    width: 10rem;
    height: 10rem;
}

.splash-circle {
    border-radius: 50%;
}

.controlled-list-splash {
    text-align: center;
    margin: 5rem 5rem 2rem 5rem;
    border: 1px solid #ddd;
    padding: 4rem 3rem;
    background: #f6f6f6;
    border-radius: 0.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.controlled-list-splash-title {
    color: #666;
    font-size: 2.8rem;
    margin-bottom: 3rem;
    margin-top: 2.5rem;
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
    padding: 2rem;
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
