<script setup>
const props = defineProps({
    action: {
        type: String,
        required: true,
    },
})

const emit = defineEmits(['close', 'confirm'])
</script>
<template>
    <div
        class="modal-confirm flex flex-col gap-6 bg-neutral-800 rounded-md p-4 items-center justify-center text-center">
        <div class="flex flex-col gap-2">
            <h2 class="border-b-1 border-yellow-300 pb-2">request received</h2>
            <span class="pt-4">{{ action }}?</span>
        </div>
        <div class="flex flex-row gap-4">
            <button class="button-style-cancel" @click="emit('close')">Cancel</button>
            <button class="button-style-confirm" @click="emit('confirm')">Confirm</button>
        </div>
    </div>
</template>