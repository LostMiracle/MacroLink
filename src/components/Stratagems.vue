<script setup>
import { ref, computed, onMounted } from 'vue'
import { DYNAMIC_MACROS, MACRO_IMAGES } from '@/data/macroData'

const props = defineProps({
    showStratagems: {
        type: Boolean,
        required: true,
        default: false
    },
    currentMacros: {
        type: Array,
        required: true,
    }
})

const emit = defineEmits(['select-stratagem'])

// Device macros from Pico
const deviceMacros = ref({})
const deviceMacroNames = ref(new Set())
const deviceDataLoaded = ref(false)

// Fetch device macros from Pico
const fetchDeviceMacros = async () => {
    try {
        const response = await fetch('/dashboard/status.json', {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        })

        if (response.ok) {
            const allData = await response.json()
            // Try to get macros from green or blue device
            const greenData = allData['green']
            const blueData = allData['blue']
            
            // Use whichever device is online
            if (greenData && !greenData.error && greenData.macros) {
                deviceMacros.value = greenData.macros
            } else if (blueData && !blueData.error && blueData.macros) {
                deviceMacros.value = blueData.macros
            }

            // Create normalized set of macro names
            deviceMacroNames.value = new Set(
                Object.keys(deviceMacros.value).map(name => name.trim().toLowerCase())
            )
        }
    } catch (error) {
        console.error('Failed to fetch device macros:', error)
        deviceMacros.value = {}
        deviceMacroNames.value = new Set()
    } finally {
        deviceDataLoaded.value = true
    }
}

// Load device macros on mount
onMounted(() => {
    fetchDeviceMacros()
})

// Convert to array for v-for with device availability check
const stratagems = computed(() => {
    return Object.keys(DYNAMIC_MACROS).map((key, index) => {
        const normalizedKey = key.toLowerCase()
        // Default to true (available) until device data is loaded
        const onDevice = !deviceDataLoaded.value || deviceMacroNames.value.has(normalizedKey)
        
        return {
            id: index + 1,
            key: key,
            name: DYNAMIC_MACROS[key],
            image: MACRO_IMAGES[key] || 'nyi.webp',
            onDevice: onDevice
        }
    })
})

const selectStratagem = (stratagem) => {
    if (!stratagem.onDevice) return // Don't select if not on device
    emit('select-stratagem', stratagem)
}

// Create a Set of current icons for O(1) lookup instead of O(n)
const currentIconsSet = computed(() => {
    return new Set(props.currentMacros.map(macro => macro.icon))
})

const isInGrid = (stratagem) => {
    const iconName = stratagem.image.replace('.webp', '')
    return currentIconsSet.value.has(iconName)
}

// Handle image load error - fallback to nyi.webp
const handleImageError = (event) => {
    event.target.src = '/images/nyi.webp'
}
</script>

<template>
    <div v-if="showStratagems"
        class="grid grid-cols-3 absolute bottom-0 left-0 right-0 top-0 items-center bg-neutral-800/98 overflow-y-auto z-10 border-t-2 border-yellow-300 grid-container">
        <button v-for="stratagem in stratagems" :key="stratagem.id"
            class="flex flex-row gap-2 items-center p-2 transition" 
            :class="[
                isInGrid(stratagem) ? 'selected-stratagem' : '',
                stratagem.onDevice ? 'cursor-pointer' : 'not-on-device cursor-not-allowed opacity-50'
            ]"
            @click="selectStratagem(stratagem)"
            :disabled="!stratagem.onDevice">
            <img :src="`/images/${stratagem.image}`" @error="handleImageError" class="w-16 h-16" :alt="stratagem.name" />
            <span class="text-tiny">{{ stratagem.name }}</span>
        </button>
    </div>
</template>

<style lang="less" scoped>
.grid-container>button {
    transition: background-color 0.2s;
    color: #fde047;
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
.grid-container>button.selected-stratagem {
    background-color: #facc15 !important;
    /* yellow-400 */
    color: black;
}

/* Not on device - disabled state */
.grid-container>button.not-on-device {
    background-color: rgba(239, 68, 68, 0.15) !important;
    /* red-500 with transparency */
    color: #f87171 !important;
    /* red-400 */
}

.grid-container>button:not(.selected-stratagem):not(.not-on-device):hover {
    background-color: rgba(64, 64, 64, 0.5);
    /* neutral-700 with transparency */
}
</style>
