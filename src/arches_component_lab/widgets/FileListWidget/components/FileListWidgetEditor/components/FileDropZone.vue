<script setup lang="ts">
import { useGettext } from "vue3-gettext";

const { $gettext } = useGettext();
</script>

<template>
    <div class="upload-container">
        <i
            class="pi pi-cloud-upload upload-icon"
            aria-hidden="true"
        />
        <div class="upload-title">
            {{ $gettext("Upload Files") }}
        </div>
        <div class="upload-subtitle">
            {{ $gettext("Drag & drop files here or click to browse") }}
        </div>
    </div>
</template>

<style scoped>
.upload-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    border: 0.125rem dashed var(--p-content-border-color);
    border-radius: 0.5rem;
    background-color: var(--p-surface-50);
    cursor: pointer;
}

.upload-icon {
    font-size: 2rem;
    color: var(--p-primary-color);
    margin-bottom: 0.5rem;
}

.upload-title {
    font-weight: bold;
    color: var(--p-text-color);
    margin-bottom: 0.25rem;
}

.upload-subtitle {
    font-size: 1rem;
    color: var(--p-text-muted-color);
}
</style>
