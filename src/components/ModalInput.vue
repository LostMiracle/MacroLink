<script setup>
import { ref } from 'vue'

const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    placeholder: {
        type: String,
        default: ''
    }
})

const emit = defineEmits(['close', 'confirm'])
const inputValue = ref('')

const handleConfirm = () => {
    emit('confirm', inputValue.value)
}
</script>

<template>
    <div class="flex flex-col gap-4 p-6 bg-neutral-800 rounded-lg min-w-[400px]">
        <h2 class="text-xl font-bold text-yellow-300">{{ title }}</h2>
        <input v-model="inputValue" type="text" :placeholder="placeholder"
            class="px-4 py-2 bg-neutral-700 border border-neutral-600 rounded text-white focus:outline-none focus:border-yellow-300"
            @keyup.enter="handleConfirm" />
        <div class="flex flex-row gap-4 justify-end">
            <button
                class="px-4 h-10 rounded cursor-pointer hover:bg-neutral-600 transition duration-200 ease-in-out select-none touch-manipulation button-style-conditional bg-neutral-800 text-yellow-300"
                @click="emit('close')">
                Cancel
            </button>
            <button
                class="px-4 h-10 rounded cursor-pointer hover:bg-green-600 transition duration-200 ease-in-out select-none touch-manipulation button-style-conditional bg-green-500 text-black"
                @click="handleConfirm">
                Save
            </button>
        </div>
    </div>
</template>
