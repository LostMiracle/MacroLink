<script setup>
import { ref, computed } from 'vue'
import { DYNAMIC_MACROS, MACRO_IMAGES } from '@/data/macroData'

// Convert to array for v-for
const stratagems = ref(
    Object.keys(DYNAMIC_MACROS).map((key, index) => ({
        id: index + 1,
        key: key,
        name: DYNAMIC_MACROS[key],
        image: MACRO_IMAGES[key]
    }))
)
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

const selectStratagem = (stratagem) => {
    emit('select-stratagem', stratagem)
}

// Create a Set of current icons for O(1) lookup instead of O(n)
const currentIconsSet = computed(() => {
    return new Set(props.currentMacros.map(macro => macro.icon))
})

const isInGrid = (stratagem) => {
    const iconName = stratagem.image.replace('.png', '')
    return currentIconsSet.value.has(iconName)
}
</script>

<template>
    <div v-if="showStratagems"
        class="grid grid-cols-3 absolute bottom-0 left-0 right-0 top-0 items-center bg-neutral-800/98 overflow-y-auto z-10 border-t-2 border-yellow-300 grid-container">
        <button v-for="stratagem in stratagems" :key="stratagem.id"
            class="flex flex-row gap-2 items-center p-2 transition cursor-pointer" @click="selectStratagem(stratagem)"
            :class="isInGrid(stratagem) ? 'selected-stratagem' : ''">
            <img :src="`/images/${stratagem.image}`" class="w-16 h-16" :alt="stratagem.name" />
            <span class="text-tiny">{{ stratagem.name }}</span>
        </button>
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
.grid-container>button.selected-stratagem {
    background-color: #facc15 !important;
    /* yellow-400 */
    color: black;
}

.grid-container>button:not(.selected-stratagem):hover {
    background-color: rgba(64, 64, 64, 0.5);
    /* neutral-700 with transparency */
}
</style>