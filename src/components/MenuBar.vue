<script setup>
import MenuControls from './MenuControls.vue'
import { useSound } from '@/composables/useSound'

const props = defineProps({
    showStratagems: {
        type: Boolean,
        required: true,
    },
    showProfiles: {
        type: Boolean,
        required: true,
    },
    showUserSelect: {
        type: Boolean,
        required: false,
        default: false
    },
    selectedUser: {
        type: String,
        required: false,
        default: 'Select User'
    },
    selectedProfile: {
        type: String,
        required: false,
        default: 'Select Profile'
    },
    removeMode: {
        type: Boolean,
        required: false,
        default: false
    }
})
const emit = defineEmits(['toggleStratagems', 'toggleProfiles', 'update:selectedUser', 'update:selectedProfile', 'trigger-remove-mode', 'select-user', 'overwrite-profile', 'save-profile', 'rename-profile', 'delete-profile'])

const { play: menuClick } = useSound('menu-open.wav')
const { play: removeModeClick } = useSound('remove-mode.mp3')
</script>

<template>
    <header class="menu-stripes flex flex-row justify-between items-center bg-neutral-800 p-4 text-sm z-99">
        <button @click="emit('toggleStratagems'), menuClick()" title="Stratagems"
            class="px-4 h-10 rounded cursor-pointer transition duration-200 ease-in-out select-none touch-manipulation button-style-conditional"
            :class="showStratagems ? 'bg-yellow-400 text-black' : 'bg-neutral-800 hover:bg-neutral-600 text-yellow-300 border-neutral-700'">
            Stratagems</button>
        <MenuControls :selected-user="selectedUser" :selected-profile="selectedProfile" :show-profiles="showProfiles"
            :show-user-select="showUserSelect" @update:selected-user="emit('update:selectedUser', $event)"
            @update:selected-profile="emit('update:selectedProfile', $event)" @toggle-profiles="emit('toggleProfiles')"
            @select-user="emit('select-user')" @overwrite-profile="emit('overwrite-profile')"
            @save-profile="emit('save-profile')" @rename-profile="emit('rename-profile')"
            @delete-profile="emit('delete-profile')" />
        <button title="Remove Mode" @click="emit('trigger-remove-mode'), removeModeClick()"
            class="px-4 h-10 rounded cursor-pointer hover:bg-neutral-600 transition duration-200 ease-in-out select-none touch-manipulation button-style-conditional"
            :class="removeMode ? 'bg-red-500 text-white' : 'bg-neutral-800 hover:bg-neutral-600 text-yellow-300 border-neutral-700'">
            Remove Mode</button>
    </header>
</template>

<style lang="less" scoped>
.menu-stripes {
    position: relative;
    background-color: rgba(24, 24, 24, 0.95);
    /* base dark */
    overflow: hidden;
    /* clip the stripes */
    max-height: max-content;
    height: auto;

    &::before {
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        /* angle, stripe width, and opacity are tunable */
        background: repeating-linear-gradient(-45deg,
                rgba(255, 255, 255, 0.10) 0 calc(10px/6),
                rgba(255, 255, 255, 0.10) calc(10px/6) calc(20px/6),
                transparent calc(20px/6) calc(30px/6),
                transparent calc(30px/6) calc(40px/6));
    }
}
</style>