<script setup>
import { ref, watch } from 'vue'

const themeElement = document.getElementById('theme-link')
const theme = ref()
watch(theme, async(theme) => {
    if (theme === 'light') {
        themeElement.setAttribute('href',"/static/node_modules/primevue/resources/themes/mdc-light-indigo/theme.css")
    }
    if (theme === 'grey') {
        themeElement.setAttribute('href',"/static/node_modules/primevue/resources/themes/bootstrap4-light-purple/theme.css")
    }
    else if (theme === 'dark') {
        themeElement.setAttribute('href',"/static/node_modules/primevue/resources/themes/mdc-dark-indigo/theme.css")
    }
})

const htmlElement = document.querySelector('html')
const direction = ref('left')
watch(direction, async(direction) => {
    if (direction === 'left') {
        htmlElement.setAttribute('dir',"ltr")
    }
    else if (direction === 'right') {
        htmlElement.setAttribute('dir',"rtl")
    }
})
</script>

<template>
    <div style="background-color: lightgray; padding: 10px; display: flex; justify-content: space-between; width: 100%; align-items: center;">
        <div>
            <button @click="theme = 'light'" style="padding: 0px;">
                <div style="width: 25px; height: 25px; background-color: white; cursor: pointer;"></div>
            </button>
            <button @click="theme = 'grey'" style="padding: 0px;">
                <div style="width: 25px; height: 25px; background-color: grey; cursor: pointer;"></div>
            </button>
            <button @click="theme = 'dark'" style="padding: 0px;">
                <div style="width: 25px; height: 25px; background-color: black; cursor: pointer;"></div>
            </button>
        </div>
        <div>
            <button 
                style="cursor: pointer;"
                @click="direction = direction === 'left' ? 'right' : 'left'"
                v-text="direction === 'left' ? 'right-to-left' : 'left-to-right'"
            ></button>
        </div>
    </div>
</template>