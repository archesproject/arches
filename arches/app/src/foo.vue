<script setup>
import { defineEmits } from 'vue';

const props = defineProps({
  title: String,
  isActive: Boolean,
  tabId: Number
});

const emit = defineEmits(['tab-selected']);

const selectTab = () => {
    if (something valid) {
        emit('tab-selected', props.tabId);
    }
};
</script>

<template>
    <button @click="selectTab" :class="{ active: isActive }">
      Title goes here
    </button>
</template>
  
