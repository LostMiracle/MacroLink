<script setup>
import { computed } from 'vue'
import { DYNAMIC_MACROS } from '@/data/macroData'

const props = defineProps({
    client: {
        type: Object,
        required: true,
    },
})

// Helper functions to format data
const formatUptime = (seconds) => {
    if (!seconds) return 'N/A'
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    return `${h}h ${m}m ${s}s`
}

const formatBytes = (bytes) => {
    if (!bytes) return 'N/A'
    if (bytes < 1024) return `${bytes} B`
    const kb = bytes / 1024
    if (kb < 1024) return `${kb.toFixed(1)} KB`
    const mb = kb / 1024
    return `${mb.toFixed(2)} MB`
}

// Computed properties for formatted data
const clientData = computed(() => {
    if (!props.client?.data) return null
    const data = props.client.data

    return {
        safe_mode: data.safe_mode ?? 'N/A',
        filesystem: data.filesystem ?? 'N/A',
        usb_mode: data.usb_mode ?? 'N/A',
        version: data.version ?? 'N/A',
        rssi: data.rssi ?? 'N/A',
        ip: data.ip ?? 'N/A',
        mac: data.mac ?? 'N/A',
        http_requests: data.http_requests ?? 'N/A',
        cpu_temp: data.cpu_temp ? `${data.cpu_temp.toFixed(1)}°C` : 'N/A',
        uptime: formatUptime(data.uptime),
        last_recovery: data.last_server_recovery
            ? `${formatUptime(data.uptime - data.last_server_recovery)} ago`
            : 'none',
        memory_used: formatBytes(data.memory?.used),
        memory_free: formatBytes(data.memory),
        memory_used_percentage: data.memory?.percent_used
            ? `${data.memory.percent_used.toFixed(1)}%`
            : 'N/A',
        last_macro_ts: data.last_macro_ts !== null
            ? `${formatUptime(data.uptime - data.last_macro_ts)} ago`
            : 'never',
    }
})

// Convert keystrokes to arrows
const keystrokesToArrows = (keystrokes) => {
    if (!keystrokes) return ''
    return keystrokes
        .replace(/w/gi, '↑')
        .replace(/a/gi, '←')
        .replace(/s/gi, '↓')
        .replace(/d/gi, '→')
}

// Macro comparison list
const macroComparison = computed(() => {
    if (!props.client?.data?.macros) return []

    // Create a set of macro names on the device (normalized to lowercase)
    const deviceMacros = props.client.data.macros || {}
    const deviceMacroNames = new Set(
        Object.keys(deviceMacros).map(name => name.trim().toLowerCase())
    )

    // Compare each macro in DYNAMIC_MACROS with device macros
    return Object.entries(DYNAMIC_MACROS).map(([key, readableName]) => {
        const normalizedKey = key.toLowerCase()
        const onDevice = deviceMacroNames.has(normalizedKey)

        const rawKeystrokes = onDevice ? deviceMacros[Object.keys(deviceMacros).find(
            k => k.trim().toLowerCase() === normalizedKey
        )] : null

        return {
            name: readableName,
            onDevice: onDevice,
            keystrokes: rawKeystrokes,
            arrows: keystrokesToArrows(rawKeystrokes)
        }
    })
})
</script>
<template>
    <div v-if="clientData"
        class="flex flex-col gap-4 p-4 bg-neutral-800 rounded-lg min-w-[500px] max-h-[80vh] overflow-y-auto max-w-3xl">
        <div class="border-b border-neutral-700 pb-2">
            <h2 class="text-xl font-bold text-yellow-300">{{ client.label }} - Details</h2>
        </div>

        <div class="grid grid-cols-4 gap-2 text-tiny">
            <div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">SAFE MODE</span>
                    <span class="text-white font-mono">{{ clientData.safe_mode }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">FILESYSTEM</span>
                    <span class="text-white font-mono">{{ clientData.filesystem }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">USB MODE</span>
                    <span class="text-white font-mono">{{ clientData.usb_mode }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">VERSION</span>
                    <span class="text-white font-mono">{{ clientData.version }}</span>
                </div>
            </div>
            <div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">RSSI</span>
                    <span class="text-white font-mono">{{ clientData.rssi }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">IP ADDRESS</span>
                    <span class="text-white font-mono">{{ clientData.ip }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">MAC ADDRESS</span>
                    <span class="text-white font-mono">{{ clientData.mac }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">HTTP REQUESTS</span>
                    <span class="text-white font-mono">{{ clientData.http_requests }}</span>
                </div>
            </div>
            <div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">CPU TEMP</span>
                    <span class="text-white font-mono">{{ clientData.cpu_temp }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">UPTIME</span>
                    <span class="text-white font-mono">{{ clientData.uptime }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">LAST RECOVERY</span>
                    <span class="text-white font-mono">{{ clientData.last_recovery }}</span>
                </div>
            </div>
            <div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">MEMORY USED</span>
                    <span class="text-white font-mono">{{ clientData.memory_used }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">MEMORY FREE</span>
                    <span class="text-white font-mono">{{ clientData.memory_free }}</span>
                </div>
                <div class="flex flex-col">
                    <span class="text-neutral-400 text-xs">MEMORY % USED</span>
                    <span class="text-white font-mono">{{ clientData.memory_used_percentage }}</span>
                </div>
            </div>
        </div>

        <!-- Macros section -->
        <div class="border-t border-neutral-700 pt-3">
            <h3 class="text-lg font-bold text-yellow-300 mb-2">Macros</h3>
            <div class="mb-3 text-xs">
                <span class="text-neutral-400">TIME SINCE LAST MACRO: </span>
                <span class="text-white font-mono">{{ clientData.last_macro_ts }}</span>
            </div>

            <div v-if="macroComparison.length > 0"
                class="grid-container grid grid-cols-3 text-xs max-h-[300px] overflow-y-auto border-1 border-neutral-700 rounded-lg">
                <div v-for="macro in macroComparison" :key="macro.name" class="flex gap-1 py-0.5 px text-tiny w-full"
                    :class="macro.onDevice ? 'text-green-400' : 'text-red-400'">
                    <div class="flex flex-col gap-1 w-full p-2">
                        <div class="flex flex-row gap-1">
                            <span class="w-3">{{ macro.onDevice ? '✓' : '✗' }}</span>
                            <span class="flex-1">{{ macro.name }}</span>
                        </div>
                        <span v-if="macro.onDevice && macro.arrows"
                            class="text-neutral-400 text-sm tracking-widest font-mono w-full">
                            [{{ macro.arrows }}]
                        </span>
                    </div>
                </div>
            </div>
            <p v-else class="text-xs text-neutral-400">No macro data available</p>
        </div>
    </div>
    <div v-else class="p-8 text-center text-neutral-400">
        No data available for this client
    </div>
</template>

<style lang="less" scoped>
.grid-container>div {
    transition: background-color 0.2s;
}

.grid-container>div:nth-child(4n + 1),
.grid-container>div:nth-child(4n + 3) {
    background-color: #ffffff05;
}

.grid-container>div:nth-child(4n + 2),
.grid-container>div:nth-child(4n + 4) {
    background-color: #ffffff10;
}
</style>