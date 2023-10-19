<script>
import { defineAsyncComponent, markRaw, inject } from 'vue'

export default {
  props: ['renderContext', 'componentType', 'componentName'],
  data(props) {
    const renderContext = props.renderContext ? props.renderContext : inject('renderContext');

    const asyncComponent = defineAsyncComponent(() =>
      import(`@/${renderContext}/${props.componentType}s/${props.componentName}.vue`)
    );

    return {
      asyncComponent: markRaw(asyncComponent)
    }
  },
}
</script>

<template>
  <component :is=asyncComponent />
</template>