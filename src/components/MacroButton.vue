<script setup>
import { MACRO_STYLES } from '@/data/macroData'
import { useSound } from '@/composables/useSound'

const props = defineProps({
    macro: {
        type: Object,
        required: true,
    },
})

// Map border color and glow from MACRO_STYLES
const getBorderColor = () => {
    const macroKey = props.macro.macroKey || ''
    const style = MACRO_STYLES[macroKey]
    const color = style?.border || 'gray'

    const colorMap = {
        'red': 'border-red-500',
        'blue': 'border-blue-500',
        'green': 'border-green-500',
        'yellow': 'border-yellow-400',
        'gray': 'border-gray-500'
    }

    return colorMap[color] || 'border-gray-500'
}

const getGlowClass = () => {
    const macroKey = props.macro.macroKey || ''
    const style = MACRO_STYLES[macroKey]
    const color = style?.border || 'gray'

    return `glow-${color}`
}

const { play: macroClick } = useSound('console-click.mp3')

const emit = defineEmits(['triggerMacro'])

const handleClick = () => {
    emit('triggerMacro', props.macro)
    macroClick()
}
</script>

<template>
    <button
        class="flex flex-col items-center rounded-lg overflow-hidden justify-center aspect-square select-none touch-manipulation cursor-pointer h-full border-2 active:scale-95 transition-transform"
        :class="[getBorderColor(), getGlowClass()]" @click="handleClick()">
        <img :src="`/images/${props.macro.icon}.png`" alt="Macro Button" class="aspect-square" />
    </button>
</template>

<style scoped>
/* Even glow on all 4 sides - no drop shadow effect */
.glow-red {
    box-shadow: 0 0 5px 2px rgba(239, 68, 68, 0.6);
}

.glow-blue {
    box-shadow: 0 0 5px 2px rgba(59, 130, 246, 0.6);
}

.glow-green {
    box-shadow: 0 0 5px 2px rgba(34, 197, 94, 0.6);
}

.glow-yellow {
    box-shadow: 0 0 5px 2px rgba(250, 204, 21, 0.6);
}

.glow-gray {
    box-shadow: 0 0 5px 2px rgba(107, 114, 128, 0.6);
}
</style>
