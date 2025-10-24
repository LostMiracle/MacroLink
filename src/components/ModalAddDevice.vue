<script setup>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'

const toast = useToast()

const props = defineProps({
    title: {
        type: String,
        default: 'Add New Device'
    }
})

const emit = defineEmits(['close', 'confirm'])

const deviceIp = ref('')
const isDiscovering = ref(false)
const isScanning = ref(false)
const discoveredDevice = ref(null)
const discoveredDevices = ref([])
const manualNetwork = ref('192.168.50')

const discoverDevice = async () => {
    if (!deviceIp.value.trim()) {
        toast.error('Please enter an IP address')
        return
    }
    
    isDiscovering.value = true
    discoveredDevice.value = null
    
    try {
        const response = await fetch(`http://${deviceIp.value.trim()}:8888/discovery`, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        })
        
        if (response.ok) {
            const deviceData = await response.json()
            discoveredDevice.value = deviceData
            toast.success(`Found device: ${deviceData.name}`)
        } else {
            toast.error('Device not found or not responding')
        }
    } catch (error) {
        console.error('Discovery failed:', error)
        toast.error('Failed to discover device. Check IP address and ensure device is online.')
    } finally {
        isDiscovering.value = false
    }
}

const handleConfirm = async () => {
    if (discoveredDevice.value) {
        try {
            // Save device to backend
            const response = await fetch('/devices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(discoveredDevice.value)
            })
            
            if (response.ok) {
                const result = await response.json()
                toast.success(`Device ${discoveredDevice.value.name} added successfully`)
                emit('confirm', discoveredDevice.value)
            } else {
                const error = await response.json()
                toast.error(error.error || 'Failed to add device')
            }
        } catch (error) {
            console.error('Failed to add device:', error)
            toast.error('Failed to add device')
        }
    }
}


const scanNetwork = async () => {
    isScanning.value = true
    discoveredDevices.value = []
    
    try {
        // Try to use mDNS discovery if available
        if (navigator.serviceWorker && 'serviceWorker' in navigator) {
            // For now, we'll scan common IP ranges since browser mDNS is limited
            await scanCommonRanges()
        } else {
            await scanCommonRanges()
        }
    } catch (error) {
        console.error('Network scan failed:', error)
        toast.error('Network scan failed')
    } finally {
        isScanning.value = false
    }
}

const scanCommonRanges = async () => {
    let rangesToScan = []
    
    // Use manual network if specified, otherwise use common ranges
    if (manualNetwork.value.trim()) {
        rangesToScan.push(manualNetwork.value.trim())
        toast.info(`Scanning network: ${manualNetwork.value.trim()}.x`)
    } else {
        // Fallback to common ranges
        rangesToScan = [
            '192.168.1', '192.168.0', '192.168.2', '192.168.4', '192.168.50',
            '10.0.0', '10.0.1', '172.16.0', '172.16.1'
        ]
        toast.info('Scanning common network ranges...')
    }
    
    const promises = []
    
    for (const range of rangesToScan) {
        for (let i = 1; i <= 254; i++) {
            const ip = `${range}.${i}`
            promises.push(checkDevice(ip))
        }
    }
    
    // Process in batches to avoid overwhelming the network
    const batchSize = 20
    for (let i = 0; i < promises.length; i += batchSize) {
        const batch = promises.slice(i, i + batchSize)
        const results = await Promise.allSettled(batch)
        
        // Add found devices to the list
        results.forEach(result => {
            if (result.status === 'fulfilled' && result.value) {
                discoveredDevices.value.push(result.value)
            }
        })
        
        // Small delay between batches
        if (i + batchSize < promises.length) {
            await new Promise(resolve => setTimeout(resolve, 100))
        }
    }
    
    if (discoveredDevices.value.length > 0) {
        toast.success(`Found ${discoveredDevices.value.length} MacroLink device(s)`)
    } else {
        toast.info('No MacroLink devices found on network')
    }
}


const checkDevice = async (ip) => {
    try {
        console.log(`Checking device at ${ip}:8888/discovery`)
        
        // Try direct request first
        let response
        try {
            response = await fetch(`http://${ip}:8888/discovery`, {
                method: 'GET',
                signal: AbortSignal.timeout(2000),
                mode: 'cors'
            })
        } catch (corsError) {
            console.log(`CORS error for ${ip}, trying with no-cors mode`)
            // Try with no-cors mode (limited but might work)
            response = await fetch(`http://${ip}:8888/discovery`, {
                method: 'GET',
                signal: AbortSignal.timeout(2000),
                mode: 'no-cors'
            })
            
            // With no-cors, we can't read the response, so we'll assume it worked
            // if we didn't get a network error
            console.log(`No-cors request to ${ip} completed`)
            return {
                name: `MacroLink-${ip.split('.').pop()}`,
                device_id: ip.split('.').pop(),
                ip: ip,
                port: 8888,
                type: 'macrolink-hid',
                version: 'unknown',
                mac: 'unknown',
                macros_count: 0
            }
        }
        
        console.log(`Response from ${ip}:`, response.status, response.ok)
        
        if (response.ok) {
            const deviceData = await response.json()
            console.log(`Device data from ${ip}:`, deviceData)
            if (deviceData.type === 'macrolink-hid') {
                console.log(`Found MacroLink device at ${ip}:`, deviceData)
                return deviceData
            }
        }
    } catch (error) {
        console.log(`Error checking ${ip}:`, error.message)
        // Device not found or not responding - this is normal
    }
    return null
}


const selectDiscoveredDevice = (device) => {
    discoveredDevice.value = device
    deviceIp.value = device.ip
}

const handleCancel = () => {
    deviceIp.value = ''
    discoveredDevice.value = null
    discoveredDevices.value = []
    emit('close')
}
</script>

<template>
    <div class="flex flex-col gap-4 p-6 bg-neutral-800 rounded-lg min-w-[500px]">
        <h2 class="text-xl font-bold text-yellow-300">{{ title }}</h2>
        
        <!-- Network Scan Section -->
        <div class="flex flex-col gap-2">
            <label class="text-sm text-neutral-300">Network Scan</label>
            <div class="flex gap-2">
                <button
                    class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded transition duration-200"
                    @click="scanNetwork"
                    :disabled="isScanning">
                    {{ isScanning ? 'Scanning...' : 'Scan for Devices' }}
                </button>
            </div>
            
            <!-- Manual Network Input -->
            <div class="flex flex-col gap-2">
                <label class="text-xs text-neutral-400">Network to scan:</label>
                <input v-model="manualNetwork" type="text" placeholder="192.168.50"
                    class="px-3 py-2 bg-neutral-700 border border-neutral-600 rounded text-white text-sm focus:outline-none focus:border-blue-300" />
            </div>
            
            <!-- Network Display -->
            <div v-if="manualNetwork.trim()" class="p-3 bg-green-900/20 border border-green-600 rounded-lg">
                <div class="text-sm">
                    <span class="text-green-300 font-bold">Will scan:</span>
                    <span class="text-white ml-2">{{ manualNetwork }}.x</span>
                </div>
            </div>
        </div>
        
        <!-- Discovered Devices List -->
        <div v-if="discoveredDevices.length > 0" class="max-h-40 overflow-y-auto">
            <h3 class="text-sm font-bold text-yellow-300 mb-2">Found Devices:</h3>
            <div class="space-y-2">
                <div v-for="device in discoveredDevices" :key="device.device_id"
                    class="p-3 bg-neutral-700 border border-neutral-600 rounded cursor-pointer hover:bg-neutral-600 transition duration-200"
                    @click="selectDiscoveredDevice(device)">
                    <div class="flex justify-between items-center">
                        <div>
                            <div class="font-bold text-white">{{ device.name }}</div>
                            <div class="text-xs text-neutral-400">{{ device.ip }} • {{ device.mac }}</div>
                        </div>
                        <div class="text-xs text-green-400">✓</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Manual IP Entry -->
        <div class="flex flex-col gap-2">
            <label class="text-sm text-neutral-300">Manual IP Entry</label>
            <div class="flex gap-2">
                <input v-model="deviceIp" type="text" placeholder="e.g., 192.168.50.100"
                    class="flex-1 px-4 py-2 bg-neutral-700 border border-neutral-600 rounded text-white focus:outline-none focus:border-yellow-300" />
                <button
                    class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition duration-200"
                    @click="discoverDevice"
                    :disabled="isDiscovering || !deviceIp.trim()">
                    {{ isDiscovering ? 'Discovering...' : 'Discover' }}
                </button>
            </div>
        </div>
        
        <!-- Discovered device info -->
        <div v-if="discoveredDevice" class="p-4 bg-green-900/20 border border-green-600 rounded-lg">
            <h3 class="text-lg font-bold text-green-300 mb-2">Device Found!</h3>
            <div class="grid grid-cols-2 gap-2 text-sm">
                <div>
                    <span class="text-neutral-400">Name:</span>
                    <span class="text-white ml-2">{{ discoveredDevice.name }}</span>
                </div>
                <div>
                    <span class="text-neutral-400">Device ID:</span>
                    <span class="text-white ml-2">{{ discoveredDevice.device_id }}</span>
                </div>
                <div>
                    <span class="text-neutral-400">Version:</span>
                    <span class="text-white ml-2">{{ discoveredDevice.version }}</span>
                </div>
                <div>
                    <span class="text-neutral-400">Type:</span>
                    <span class="text-white ml-2">{{ discoveredDevice.type }}</span>
                </div>
                <div>
                    <span class="text-neutral-400">MAC:</span>
                    <span class="text-white ml-2">{{ discoveredDevice.mac }}</span>
                </div>
                <div>
                    <span class="text-neutral-400">Macros:</span>
                    <span class="text-white ml-2">{{ discoveredDevice.macros_count }}</span>
                </div>
            </div>
        </div>
        
        <div class="flex flex-row gap-4 justify-end">
            <button
                class="px-4 h-10 rounded cursor-pointer hover:bg-neutral-600 transition duration-200 ease-in-out select-none touch-manipulation button-style-conditional bg-neutral-800 text-yellow-300"
                @click="handleCancel">
                Cancel
            </button>
            <button
                class="px-4 h-10 rounded cursor-pointer hover:bg-green-600 transition duration-200 ease-in-out select-none touch-manipulation button-style-conditional bg-green-500 text-black"
                @click="handleConfirm"
                :disabled="!discoveredDevice">
                Add Device
            </button>
        </div>
    </div>
</template>
