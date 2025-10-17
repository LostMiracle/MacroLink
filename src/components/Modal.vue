<script setup>
const emit = defineEmits(['close'])
</script>

<template>
    <div class="fixed inset-0 flex justify-center items-center z-50 bg-neutral-900/90" @click.self="emit('close')">
        <slot />
    </div>
</template>
