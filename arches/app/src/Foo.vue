<script setup>
  import GenericLoader from 'GenericLoader.vue';
  import { shallowRef } from 'vue'

  const componentType = shallowRef('widget')
  const componentName = shallowRef('Bar')
</script>

<template>
  <GenericLoader :componentType="componentType" :componentName="componentName"/>
</template>
