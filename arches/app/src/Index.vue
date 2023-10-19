<script>
    import { shallowRef } from 'vue'
    import SplashPage from '@/SplashPage.vue';
    import UserDashboard from '@/UserDashboard.vue';

    const user = shallowRef('permissioned');
    // const user = shallowRef('non-permissioned');

    export default{
        components: {
            UserDashboard,
            SplashPage,
        },
        data() {
            return {
                user: user,
                count: 1
            }
        },
        methods: {
            increment() {
                this.count += 1;
                return this.count;
            },
            decrement() {
                this.count -= 1;
                return this.count;
            }
        },
    }
</script>

<template>
    {{ $gettext("My message") }}
    <p>
        {{ $ngettext("%{c} result found.", "%{c} results found.", count, { c: count }) }}
    </p>
    <button @click="increment">Update search resutls</button>
    <button @click="decrement">Decrease search resutls</button>
    <div style="height: 100vh;">
        <UserDashboard v-if="user === 'permissioned'" />
        <SplashPage v-else />
    </div>
</template>
