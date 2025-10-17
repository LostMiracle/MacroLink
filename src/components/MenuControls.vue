<script setup>
import { ref, watch, computed } from 'vue'
import { useSound } from '@/composables/useSound'
import { useToast } from 'vue-toastification'

const props = defineProps({
    selectedUser: {
        type: String,
        required: false,
        default: ''
    },
    selectedProfile: {
        type: String,
        required: false,
        default: ''
    },
    showProfiles: {
        type: Boolean,
        required: false,
        default: false
    },
    showUserSelect: {
        type: Boolean,
        required: false,
        default: false
    }
})

const emit = defineEmits(['update:selectedUser', 'update:selectedProfile', 'toggleProfiles', 'selectUser', 'overwriteProfile', 'saveProfile', 'renameProfile', 'deleteProfile'])

const users = [
    { value: 'green', label: 'Helldiver Green', color: 'text-green-400', jsonKey: 'user1' },
    { value: 'blue', label: 'Helldiver Blue', color: 'text-blue-400', jsonKey: 'user2' }
]

// Get display label for selected user
const selectedUserLabel = computed(() => {
    const user = users.find(u => u.value === props.selectedUser)
    return user ? user.label : 'Select User'
})

const profiles = ref([])
const loadingProfiles = ref(false)
const allProfilesData = ref({})

// Load profiles.json once
const loadProfilesData = async () => {
    try {
        const response = await fetch('/all_profiles')
        allProfilesData.value = await response.json()
    } catch (error) {
        console.error('Failed to load profiles:', error)
        allProfilesData.value = {}
    }
}

// Load on mount
loadProfilesData()

// Get profiles for selected user
watch(() => props.selectedUser, (newUser) => {
    if (!newUser) {
        profiles.value = []
        return
    }

    // Map green/blue to user1/user2
    const userObj = users.find(u => u.value === newUser)
    const jsonKey = userObj ? userObj.jsonKey : newUser

    const userProfiles = allProfilesData.value[jsonKey] || {}
    profiles.value = Object.keys(userProfiles)
}, { immediate: true })

const handleUserChange = (event) => {
    emit('update:selectedUser', event.target.value)
    emit('update:selectedProfile', '') // Clear profile when user changes
}

const selectedUserColor = computed(() => {
    if (!props.selectedUser) return 'bg-neutral-800 hover:bg-neutral-600 text-yellow-300'

    const user = users.find(u => u.value === props.selectedUser)
    if (user?.value === 'green') {
        return 'border-green-500/50 text-green-500 bg-neutral-800'
    } else if (user?.value === 'blue') {
        return 'border-blue-500/50 text-blue-500 bg-neutral-800'
    }
    return 'bg-neutral-800 hover:bg-neutral-600 text-yellow-300 border-neutral-700'
})

const handleOverwrite = () => {
    emit('overwriteProfile')
}

const handleSave = () => {
    emit('saveProfile')
}

const handleRename = () => {
    emit('renameProfile')
}

const handleDelete = () => {
    emit('deleteProfile')
}

const { play: menuClick } = useSound('menu-open.wav')
</script>

<template>
    <div class="flex flex-row gap-2">
        <div class="flex flex-row gap-2">
            <button name="user" @click="emit('selectUser'), menuClick()" :value="selectedUser"
                @change="handleUserChange" class=" px-4 h-10 rounded cursor-pointer hover:bg-neutral-600 transition duration-200 ease-in-out
                select-none touch-manipulation button-style-conditional" :class="selectedUserColor">
                {{ selectedUserLabel }}
            </button>
            <button name="profile" @click="emit('toggleProfiles'), menuClick()" :disabled="!selectedUser"
                class="px-4 h-10 rounded cursor-pointer transition duration-200 ease-in-out select-none touch-manipulation disabled:opacity-50 disabled:cursor-not-allowed min-w-[175px] button-style-conditional"
                :class="showProfiles ? 'bg-yellow-400 text-black' : 'bg-neutral-800 hover:bg-neutral-600 text-yellow-300 border-neutral-700'">
                {{ selectedProfile || 'Select Loadout' }}
            </button>
        </div>
        <div class="flex flex-row gap-2">
            <button
                class="w-10 h-10 flex items-center justify-center rounded text-neutral-400 hover:text-cyan-300 transition duration-200 ease-in-out cursor-pointer select-none touch-manipulation button-style-icon"
                title="Overwrite" @click="handleOverwrite">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                    class="w-5 h-5">
                    <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
                </svg>
            </button>
            <button
                class="w-10 h-10 flex items-center justify-center rounded text-neutral-400 hover:text-green-300 transition duration-200 ease-in-out cursor-pointer select-none touch-manipulation button-style-icon"
                title="Save" @click="handleSave">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                    class="w-5 h-5">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                    <polyline points="17 21 17 13 7 13 7 21" />
                    <polyline points="7 3 7 8 15 8" />
                </svg>
            </button>
            <button
                class="w-10 h-10 flex items-center justify-center rounded text-neutral-400 hover:text-amber-300 transition duration-200 ease-in-out cursor-pointer select-none touch-manipulation button-style-icon"
                title="Rename" @click="handleRename">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                    class="w-5 h-5">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
            </button>
            <button
                class="w-10 h-10 flex items-center justify-center rounded text-neutral-400 hover:text-red-300 transition duration-200 ease-in-out cursor-pointer select-none touch-manipulation button-style-icon"
                title="Delete" @click="handleDelete">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                    class="w-5 h-5">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    <line x1="10" y1="11" x2="10" y2="17" />
                    <line x1="14" y1="11" x2="14" y2="17" />
                </svg>
            </button>
        </div>
    </div>
</template>
