<script setup>
import { ref, onMounted } from 'vue'
import DashboardClient from '../components/DashboardClient.vue'
import DashboardClientData from '../components/DashboardClientData.vue'
import Modal from '../components/Modal.vue'
import ModalConfirm from '../components/ModalConfirm.vue'
import ModalInput from '../components/ModalInput.vue'
import ModalAddDevice from '../components/ModalAddDevice.vue'
import { useToast, POSITION } from 'vue-toastification'

const toast = useToast()

const clients = ref([
  { id: 'green', label: 'Green MacroLink', status: 'offline', data: null },
  { id: 'blue', label: 'Blue MacroLink', status: 'offline', data: null },
])

const showClientData = ref(false)
const selectedClient = ref(null)
const showRebootConfirm = ref(false)
const clientToReboot = ref(null)
const showAddDevice = ref(false)
const showRenameDevice = ref(false)
const deviceToRename = ref(null)

const checkAllClients = async () => {
  try {
    const response = await fetch('/dashboard/status.json', {
      method: 'GET',
      signal: AbortSignal.timeout(5000)
    })

    if (response.ok) {
      const allData = await response.json()
      toast.info('Dashboard refreshed.', {
        position: POSITION.BOTTOM_CENTER,
        timeout: 5000,
        hideProgressBar: false,
        toastClassName: ' compact-toast'
      })
      console.log(allData)

      // Update each client based on Flask response
      clients.value.forEach(client => {
        const clientData = allData[client.id]

        if (clientData && !clientData.error) {
          client.status = 'online'
          client.data = clientData
        } else {
          client.status = 'offline'
          client.data = null
        }
      })
    } else {
      // Mark all offline if Flask request fails
      clients.value.forEach(client => {
        client.status = 'offline'
        client.data = null
      })
    }
  } catch (error) {
    console.error('Failed to fetch dashboard status:', error)
    clients.value.forEach(client => {
      client.status = 'offline'
      client.data = null
    })
  }
}

// Reboot handler - show confirm modal
const handleReboot = (client) => {
  console.log('handleReboot called', client, 'showRebootConfirm will be:', true)
  if (!client.data?.ip) {
    toast.error('No IP address for client')
    return
  }

  clientToReboot.value = client
  showRebootConfirm.value = true
  console.log('showRebootConfirm is now:', showRebootConfirm.value)
}

// Actually perform the reboot after confirmation
const confirmReboot = async () => {
  const client = clientToReboot.value
  showRebootConfirm.value = false

  if (!client) return

  try {
    const response = await fetch(`http://${client.data.ip}:8888/system/reboot`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000)
    })

    if (response.ok) {
      const text = await response.text()
      toast.success(`${client.label} reboot requested`, {
        toastClassName: 'compact-toast'
      })
      // Refresh status after a delay
      setTimeout(checkAllClients, 3000)
    } else {
      toast.error(`Failed to reboot ${client.label}`)
    }
  } catch (error) {
    console.error(`Error rebooting ${client.label}:`, error)
    toast.error(`Error rebooting ${client.label}`)
  } finally {
    clientToReboot.value = null
  }
}

// Client info handler
const handleClientInfo = (client) => {
  selectedClient.value = client
  showClientData.value = true
}

// Add device handler
const handleAddDevice = async (deviceData) => {
  try {
    // Check if device already exists locally
    const existingDevice = clients.value.find(client => 
      client.id === deviceData.device_id || 
      client.label === deviceData.name ||
      (client.data && client.data.ip === deviceData.ip)
    )
    
    if (existingDevice) {
      toast.error(`Device ${deviceData.name} already exists`)
      return
    }
    
    // Add the new device to the clients array (device is already saved to backend by ModalAddDevice)
    const newClient = {
      id: deviceData.device_id,
      label: deviceData.name,
      status: 'offline',
      data: null
    }
    clients.value.push(newClient)
    
    showAddDevice.value = false
    
    // Check status of the new device
    setTimeout(checkAllClients, 1000)
  } catch (error) {
    console.error('Failed to add device:', error)
    toast.error('Failed to add device')
  }
}

// Rename device handler
const handleRenameDevice = (client) => {
  deviceToRename.value = client
  showRenameDevice.value = true
}

// Confirm rename
const confirmRename = async (newName) => {
  if (!deviceToRename.value || !newName.trim()) return
  
  try {
    // Check if this is a static device (green/blue) or a saved device
    if (deviceToRename.value.id === 'green' || deviceToRename.value.id === 'blue') {
      // Static devices - just update locally (no backend save needed)
      deviceToRename.value.label = newName.trim()
      toast.success(`Device renamed to ${newName}`)
      showRenameDevice.value = false
      deviceToRename.value = null
    } else {
      // Saved device - update in backend
      const response = await fetch(`/devices/${deviceToRename.value.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: newName.trim() })
      })
      
      if (response.ok) {
        // Update the client label locally
        deviceToRename.value.label = newName.trim()
        toast.success(`Device renamed to ${newName}`)
        showRenameDevice.value = false
        deviceToRename.value = null
      } else {
        const error = await response.json()
        toast.error(error.error || 'Failed to rename device')
      }
    }
  } catch (error) {
    console.error('Failed to rename device:', error)
    toast.error('Failed to rename device')
  }
}

// Load saved devices from backend
const loadSavedDevices = async () => {
  try {
    const response = await fetch('/devices')
    if (response.ok) {
      const savedDevices = await response.json()
      
      // Add saved devices to clients array (after static ones)
      savedDevices.forEach(device => {
        const newClient = {
          id: device.id,
          label: device.name,
          status: 'offline',
          data: null
        }
        clients.value.push(newClient)
      })
      
      console.log(`Loaded ${savedDevices.length} saved devices`)
    }
  } catch (error) {
    console.error('Failed to load saved devices:', error)
  }
}

// Check on mount
onMounted(() => {
  loadSavedDevices()
  checkAllClients()
})
</script>

<template>
  <div class="dashboard flex flex-col h-full">
    <div class="flex flex-row justify-between p-4 items-center menu-stripes">
      <h2 class="text-2xl font-bold">MACROLINK DASHBOARD</h2>
      <div class="flex flex-row gap-4 items-center">
        <button class="button-style text-sm" @click="checkAllClients">Refresh</button>
        <button class="button-style text-sm" @click="showAddDevice = true">Add Device</button>
        <router-link to="/"><button class="button-style text-sm">Macro
            Panel</button></router-link>
      </div>
    </div>
    <div class="p-4 flex flex-col gap-4">
      <DashboardClient v-for="client in clients" :key="client.label" :client="client" @reboot="handleReboot(client)"
        @clientInfo="handleClientInfo(client)" @rename="handleRenameDevice(client)" />
    </div>
  </div>

  <!-- Modal for client data - outside dashboard container -->
  <Transition name="fade">
    <Modal v-if="showClientData" @close="showClientData = false">
      <DashboardClientData :client="selectedClient" />
    </Modal>
  </Transition>

  <!-- Modal for reboot confirmation -->
  <Transition name="fade">
    <Modal v-if="showRebootConfirm" @close="showRebootConfirm = false">
      <ModalConfirm :action="`reboot ${clientToReboot?.label}`" @close="showRebootConfirm = false"
        @confirm="confirmReboot" />
    </Modal>
  </Transition>

  <!-- Modal for adding devices -->
  <Transition name="fade">
    <Modal v-if="showAddDevice" @close="showAddDevice = false">
      <ModalAddDevice @close="showAddDevice = false" @confirm="handleAddDevice" />
    </Modal>
  </Transition>

  <!-- Modal for renaming devices -->
  <Transition name="fade">
    <Modal v-if="showRenameDevice" @close="showRenameDevice = false">
      <ModalInput 
        title="Rename Device" 
        :placeholder="deviceToRename?.label || 'Enter new name'"
        @close="showRenameDevice = false" 
        @confirm="confirmRename" />
    </Modal>
  </Transition>
  <!-- detail text-->
  <div
    class="absolute bottom-0 left-0 right-0 text-center px-2 text-[8px] flex flex-row justify-between text-yellow-300 font-thin opacity-50 z-5">
    <div><router-link to="/dashboard">
        <span class="text-[12px]">> ::</span> REMOTE COMMAND<span class="text-[12px]">:</span> SUPER DESTROYER //
        SIGNAL<span class="text-[12px]">:</span> ALL CLEAR // REQUEST<span class="text-[12px]">:</span> ENGAGE
      </router-link>
    </div>
    <div><span class="text-[12px]">::</span> STRATAGEM ARRAY STANDBY <span class="text-[12px]">::</span>
      CMD_QUEUE<span class="text-[12px]">:</span> IDLE // READY FOR DEPLOYMENT</div>
  </div>
</template>

<style lang="less" scoped>
.menu-stripes {
  position: relative;
  background-color: rgba(24, 24, 24, 0.95);
  /* base dark */
  overflow: hidden;
  /* clip the stripes */

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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>