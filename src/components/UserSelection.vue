<script setup>
import UserSelect from './UserSelect.vue'

const emit = defineEmits(['selectUser'])

const selectUser = (user) => {
    emit('selectUser', user)
}
</script>

<template>
    <div class="user-select bg-neutral-800 p-6 rounded-lg flex flex-col">
        <div class="user-select-header mb-4">
            <h2 class="text-2xl font-bold text-center border-b border-yellow-300 pb-4">Select User</h2>
        </div>
        <div class="user-select-body flex flex-col gap-4 mt-2">
            <UserSelect @select-user="selectUser" />
        </div>
    </div>
</template>