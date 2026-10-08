<script setup lang="ts" generic="Value extends string">
import Button from "openvue/button";

const SELECT_EVENT = "select" as const;

const { options, activeValue } = defineProps<{
    options: { value: Value; label: string; icon: string }[];
    activeValue: Value | null;
}>();

const emit = defineEmits<{
    (event: typeof SELECT_EVENT, value: Value): void;
}>();
</script>

<template>
    <div class="tool-button-group">
        <Button
            v-for="option in options"
            :key="option.value"
            class="tool-button"
            :class="{ 'tool-button-active': option.value === activeValue }"
            :outlined="true"
            :aria-pressed="option.value === activeValue"
            @click="emit(SELECT_EVENT, option.value)"
        >
            <i
                aria-hidden="true"
                :class="option.icon"
            />
            <span>{{ option.label }}</span>
        </Button>
    </div>
</template>

<style scoped>
.tool-button-group {
    display: flex;
    gap: 0.65rem;
}

.tool-button {
    flex: 1;
    flex-direction: column;
    gap: 0.5rem;
    padding-block: 0.9rem;
    padding-inline: 0.3rem;
    border-width: 0.15rem;
    border-color: var(--p-content-border-color);
    border-radius: 0.65rem;
    color: var(--p-text-muted-color);
    font-size: 1.1rem;
    font-weight: 600;
    line-height: 1;
}

.tool-button .pi {
    font-size: 1.7rem;
}

.tool-button.tool-button-active {
    border-color: var(--p-primary-color);
    background: var(--p-highlight-background);
    color: var(--p-primary-color);
}
</style>
