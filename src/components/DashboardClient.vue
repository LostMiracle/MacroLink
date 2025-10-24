<script setup>
import { ref } from 'vue'

const props = defineProps({
    client: {
        type: Object,
        required: true,
    },
})

const emit = defineEmits(['reboot', 'clientInfo', 'rename'])

const clientInfo = () => {
    emit('clientInfo')
}

const renameClient = () => {
    emit('rename')
}

const showClientData = ref(false)
</script>

<template>
    <div class="flex flex-row justify-between p-2 bg-neutral-800 border-neutral-700 border-1 rounded-md items-center">
        <span :class="client.label === 'Green MacroLink' ? 'text-green-400' : 'text-blue-400'">{{ client.label }}</span>
        <div class="flex flex-row gap-2 items-center">
            <span class="mr-4" :class="client.status === 'online' ? 'text-green-400' : 'text-red-400'">{{ client.status
            }}</span>
            <button
                class="px-4 h-10 rounded transition duration-200 ease-in-out select-none touch-manipulation button-style-conditional bg-neutral-800"
                @click="clientInfo" :disabled="client.status === 'offline'"
                :class="client.status === 'online' ? 'opacity-100 text-yellow-300 border-neutral-700 hover:bg-neutral-600 cursor-pointer' : 'opacity-50 border-red-400 text-red-400 cursor-not-allowed'">
                INFO
            </button>
            <button
                class="px-4 h-10 rounded transition duration-200 ease-in-out select-none touch-manipulation button-style-conditional bg-neutral-800"
                @click="renameClient"
                :class="'opacity-100 text-blue-300 border-neutral-700 hover:bg-neutral-600 cursor-pointer'">
                Rename
            </button>
            <button
                class="px-4 h-10 rounded transition duration-200 ease-in-out select-none touch-manipulation button-style-conditional bg-neutral-800"
                @click="emit('reboot')" :disabled="client.status === 'offline'"
                :class="client.status === 'online' ? 'opacity-100 text-yellow-300 border-neutral-700 hover:bg-neutral-600 cursor-pointer' : 'opacity-50 border-red-400 text-red-400 cursor-not-allowed'">
                Reboot
            </button>
        </div>
    </div>
</template>