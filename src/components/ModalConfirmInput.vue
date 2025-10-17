<script setup>
import { ref } from 'vue'

const props = defineProps({
    action: {
        type: String,
        required: true,
    },
    placeholder: {
        type: String,
        default: 'Enter Loadout Name'
    }
})

const emit = defineEmits(['close', 'confirm'])
const input = ref('')

const handleConfirm = () => {
    emit('confirm', input.value)
}
</script>
<template>
    <div
        class="modal-confirm flex flex-col gap-6 bg-neutral-800 rounded-md p-4 items-center justify-center text-center">
        <div class="flex flex-col gap-2">
            <h2 class="border-b-1 border-yellow-300 pb-2">request received</h2>
            <span class="pt-4">{{ action }}?</span>
        </div>
        <input type="text" v-model="input" :placeholder="placeholder"
            class="px-4 py-2 bg-neutral-700 border border-neutral-600 rounded text-white focus:outline-none focus:border-yellow-300"
            @keyup.enter="handleConfirm" />
        <div class="flex flex-row gap-4">
            <button class="button-style-cancel" @click="emit('close')">Cancel</button>
            <button class="button-style-confirm" @click="handleConfirm">Save</button>
        </div>
    </div>
</template>