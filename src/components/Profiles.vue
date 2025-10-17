<script setup>
import { ref, computed, watch } from 'vue'
import { MACRO_IMAGES } from '@/data/macroData'

const userMap = {
    'green': 'user1',
    'blue': 'user2'
}

const props = defineProps({
    showProfiles: {
        type: Boolean,
        required: true,
    },
    selectedProfile: {
        type: String,
        required: false,
        default: ''
    },
    selectedUser: {
        type: String,
        required: false,
        default: ''
    }
})

const allProfilesData = ref({})

const loadProfilesData = async () => {
    try {
        const response = await fetch('/all_profiles')
        allProfilesData.value = await response.json()
        console.log('Loading profiles:', allProfilesData.value)
    } catch (error) {
        console.error('Failed to load profiles:', error)
    }
}

loadProfilesData()

const profiles = ref([])

// Function to rebuild profiles list
const rebuildProfiles = () => {
    if (!props.selectedUser) {
        profiles.value = []
        return
    }

    const jsonKey = userMap[props.selectedUser]
    const userProfiles = allProfilesData.value[jsonKey] || {}

    console.log('User:', props.selectedUser, 'jsonKey:', jsonKey, 'userProfiles:', userProfiles)

    // Convert to array with profile name and macros
    profiles.value = Object.keys(userProfiles).map((profileName, index) => {
        const macroKeys = userProfiles[profileName] || []

        // Get images for each macro (skip Reinforce and Resupply, only show first 8)
        const macroImages = macroKeys
            .filter(key => key !== 'Reinforce' && key !== 'Resupply')
            .slice(0, 8)
            .map(key => {
                const imageFile = MACRO_IMAGES[key]
                return imageFile ? imageFile : null
            })
            .filter(img => img !== null)

        return {
            id: index + 1,
            name: profileName,
            macros: macroImages
        }
    })

    console.log('Profiles with images:', profiles.value)
}

// Watch for user changes
watch(() => props.selectedUser, rebuildProfiles, { immediate: true })

// Also watch for when data loads
watch(allProfilesData, rebuildProfiles, { deep: true })

const emit = defineEmits(['select-profile'])

const selectProfile = (profile) => {
    emit('select-profile', profile.name)
}

const isSelected = (profile) => {
    return props.selectedProfile === profile.name
}
</script>

<template>
    <div v-if="showProfiles"
        class="absolute bottom-0 left-0 right-0 top-0 bg-neutral-800/98 z-10 border-t-2 border-yellow-300">
        <div class="absolute top-0 left-0 right-0 z-20"></div>
        <div class="absolute inset-0 overflow-y-auto pt-2">
            <div class="grid grid-cols-3 grid-container">
                <button v-for="profile in profiles" :key="profile.id" @click="selectProfile(profile)"
                    class="flex flex-col gap-2 p-3 transition cursor-pointer"
                    :class="isSelected(profile) ? 'selected-profile' : ''">
                    <span class="text-start text-sm pb-1"
                        :class="isSelected(profile) ? 'border-b border-black' : 'border-b border-yellow-200/25'">{{
                            profile.name
                        }}</span>
                    <div class="grid grid-cols-8 gap-2 w-fit">
                        <img v-for="(image, idx) in profile.macros" :key="idx" :src="`/images/${image}`" class="w-6 h-6"
                            :alt="image" />
                    </div>
                </button>
            </div>
        </div>
    </div>
</template>

<style lang="less" scoped>
.grid-container>button {
    transition: background-color 0.2s;
}

.grid-container>button:nth-child(4n + 1),
.grid-container>button:nth-child(4n + 3) {
    background-color: #ffffff05;
}

.grid-container>button:nth-child(4n + 2),
.grid-container>button:nth-child(4n + 4) {
    background-color: #ffffff10;
}

/* Selected state - higher specificity wins */
.grid-container>button.selected-profile {
    background-color: #facc15 !important;
    /* yellow-400 */
    color: black;
}

.grid-container>button:not(.selected-profile):hover {
    background-color: rgba(64, 64, 64, 0.5);
    /* neutral-700 with transparency */
}
</style>