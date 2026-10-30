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
            <div class="splash-note">
                {{
                    $gettext(
                        "Use the Controlled List Manager to create new lists of " +
                            "controlled vocabularies, or update an existing list by " +
                            "selecting it from the tree in the sidebar. Use Arches " +
                            "Designer to select which node(s) in a model can use a list.",
                    )
                }}
            </div>
        </div>
    </div>
</template>

<style scoped>
.splash-large {
    width: 7.5rem;
    height: 7.5rem;
}

.splash-circle {
    border-radius: 50%;
}

.controlled-list-splash {
    text-align: center;
    margin: 5rem 5rem 2rem 5rem;
    border: 1px solid #ddd;
    padding: 10rem 3rem;
    background: var(--p-content-hover-background);
    border-radius: var(--p-content-border-radius);
    display: flex;
    flex-direction: column;
    align-items: center;
}

.controlled-list-splash-title {
    font-size: 2.8rem;
    margin-bottom: 0.5rem;
    margin-top: 4rem;
}

.splash-note {
    max-width: 150ch;
}

i {
    color: steelblue;
    font-size: x-large;
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
    line-height: 1.15;
    font-weight: 400;
    padding: 0 10rem;
    margin-bottom: 10rem;
}
</style>
