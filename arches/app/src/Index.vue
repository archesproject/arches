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
                user: user
            }
        }
    }
</script>

<template>
    <div style="height: 100vh;">
        <UserDashboard v-if="user === 'permissioned'" />
        <SplashPage v-else />
    </div>
</template>
