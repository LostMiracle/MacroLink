<script setup>
import { ref } from 'vue'
import { useSound } from '@/composables/useSound'

const emit = defineEmits(['selectUser'])

const users = ref([
    { value: 'green', label: 'Helldiver Green', class: 'bg-green-500 text-black px-4 py-2 rounded-md shadow-sm shadow-black/50' },
    { value: 'blue', label: 'Helldiver Blue', class: 'bg-blue-500 text-black px-4 py-2 rounded-md shadow-sm shadow-black/50' }
])

const selectUser = (user) => {
    console.log(user)
}
const { play: loginClick } = useSound('login.mp3')
</script>

<template>
    <button v-for="user in users" :key="user.value" @click="emit('selectUser', user.value), loginClick()"
        :class="user.class">{{
            user.label }}</button>
</template>