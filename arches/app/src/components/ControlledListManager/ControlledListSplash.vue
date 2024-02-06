<script setup lang="ts">
import { useGettext } from "vue3-gettext";

const props: { description: string } = defineProps(["description"]);

const { $gettext } = useGettext();
</script>

<template>
    <div
        id="rr-splash"
        class="rr-splash"
    >
        <!-- Image -->
        <div
            aria-hidden="true"
            class="img-lg img-circle rr-splash-img-container"
        >
            <i class="fa fa-list" />
        </div>

        <!-- Splash Title -->
        <div class="rr-splash-title">
            {{ $gettext("Welcome to Arches' Controlled List Manager") }}
        </div>

        <!-- Splash Instructions -->
        <div class="rr-splash-description">
            {{ props.description }}
        </div>
    </div>
</template>
