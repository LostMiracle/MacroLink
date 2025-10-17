<script setup>
import MainGrid from '../components/MainGrid.vue'
import MenuBar from '../components/MenuBar.vue'
import { ref } from 'vue'
import { useMacrolinkStore } from '@/stores/macrolink'
import { useToast, POSITION } from 'vue-toastification'
import { storeToRefs } from 'pinia'
import Modal from '../components/Modal.vue'
import ModalConfirm from '../components/ModalConfirm.vue'
import ModalConfirmInput from '../components/ModalConfirmInput.vue'
import UserSelection from '../components/UserSelection.vue'

const store = useMacrolinkStore()
const toast = useToast()

// Use storeToRefs to keep reactivity
const {
  showStratagems,
  showProfiles,
  removeMode,
  selectedUser,
  selectedProfile,
  showUserSelect,
  macros
} = storeToRefs(store)

const showOverwriteConfirm = ref(false)
const showSavePrompt = ref(false)
const showRenamePrompt = ref(false)
const showDeleteConfirm = ref(false)
const newProfileName = ref('')

let removeTimerId = null
let removeToastShown = false

const triggerRemoveMode = () => {
  // If already active, turn off immediately
  if (removeMode.value) {
    store.setRemoveMode() // Turn off
    if (removeTimerId) clearTimeout(removeTimerId)
    removeTimerId = null
    removeToastShown = false
    return
  }

  // Turn on
  store.setRemoveMode()

  if (!removeToastShown) {
    toast.info('Tap macros to remove.', {
      position: POSITION.BOTTOM_CENTER,
      timeout: 5000,
      hideProgressBar: true,
      toastClassName: ' compact-toast'
    })
    removeToastShown = true
  }

  // Start timer
  startRemoveTimer()
}

const startRemoveTimer = () => {
  // Reset timer
  if (removeTimerId) clearTimeout(removeTimerId)
  removeTimerId = setTimeout(() => {
    if (removeMode.value) {
      store.setRemoveMode() // Turn off
    }
    removeTimerId = null
    removeToastShown = false
  }, 5000)
}

const handleSelectUser = (userValue) => {
  store.setSelectedUser(userValue)
  store.toggleUserSelect()
}

// Handle overwrite profile button
const handleOverwrite = () => {
  if (!selectedUser.value || !selectedProfile.value) {
    toast.warning('Select a user and profile first')
    return
  }
  showOverwriteConfirm.value = true
}

// Confirm and execute overwrite
const confirmOverwrite = async () => {
  showOverwriteConfirm.value = false

  const userKey = selectedUser.value === 'green' ? 'user1' : 'user2'
  const currentMacros = macros.value.map(m => m.macroKey)

  try {
    const response = await fetch('/save_profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user: userKey,
        profile: selectedProfile.value.toLowerCase(),
        macros: currentMacros
      })
    })

    if (response.ok) {
      const data = await response.json()
      toast.success(`Loadout '${selectedProfile.value}' updated`, {
        toastClassName: 'compact-toast'
      })
    } else {
      toast.error('Failed to save profile')
    }
  } catch (error) {
    console.error('Error saving profile:', error)
    toast.error('Failed to save profile')
  }
}

// Handle save as new profile
const handleSave = () => {
  if (!selectedUser.value) {
    toast.warning('Select a user first')
    return
  }
  newProfileName.value = ''
  showSavePrompt.value = true
}

// Handle rename profile
const handleRename = () => {
  if (!selectedUser.value || !selectedProfile.value) {
    toast.warning('Select a user and profile first')
    return
  }
  newProfileName.value = selectedProfile.value
  showRenamePrompt.value = true
}

// Handle delete profile
const handleDelete = () => {
  if (!selectedUser.value || !selectedProfile.value) {
    toast.warning('Select a user and profile first')
    return
  }
  showDeleteConfirm.value = true
}

// Confirm and execute save
const confirmSave = async (profileName) => {
  if (!profileName || !profileName.trim()) {
    toast.warning('Enter a profile name')
    return
  }

  showSavePrompt.value = false

  const userKey = selectedUser.value === 'green' ? 'user1' : 'user2'
  const currentMacros = macros.value.map(m => m.macroKey)

  try {
    const response = await fetch('/save_profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user: userKey,
        profile: profileName.trim().toLowerCase(),
        macros: currentMacros
      })
    })

    if (response.ok) {
      const data = await response.json()
      toast.success(`Loadout '${profileName}' saved`, {
        toastClassName: 'compact-toast'
      })
      // Select the newly saved profile
      store.setSelectedProfile(profileName.trim().toLowerCase())
    } else {
      toast.error('Failed to save profile')
    }
  } catch (error) {
    console.error('Error saving profile:', error)
    toast.error('Failed to save profile')
  }
}

// Confirm and execute rename
const confirmRename = async (newName) => {
  if (!newName || !newName.trim()) {
    toast.warning('Enter a profile name')
    return
  }

  if (newName.trim().toLowerCase() === selectedProfile.value.toLowerCase()) {
    toast.warning('New name must be different')
    showRenamePrompt.value = false
    return
  }

  showRenamePrompt.value = false

  const userKey = selectedUser.value === 'green' ? 'user1' : 'user2'

  try {
    const response = await fetch('/rename_profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user: userKey,
        old_profile: selectedProfile.value.toLowerCase(),
        new_profile: newName.trim().toLowerCase()
      })
    })

    if (response.ok) {
      const data = await response.json()
      toast.success(`Loadout renamed to '${newName}'`, {
        toastClassName: 'compact-toast'
      })
      // Select the renamed profile
      store.setSelectedProfile(newName.trim().toLowerCase())
    } else {
      toast.error('Failed to rename profile')
    }
  } catch (error) {
    console.error('Error renaming profile:', error)
    toast.error('Failed to rename profile')
  }
}

// Confirm and execute delete
const confirmDelete = async () => {
  showDeleteConfirm.value = false

  const userKey = selectedUser.value === 'green' ? 'user1' : 'user2'
  const profileToDelete = selectedProfile.value

  try {
    const response = await fetch('/delete_profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user: userKey,
        profile: profileToDelete.toLowerCase()
      })
    })

    if (response.ok) {
      const data = await response.json()
      toast.success(`Loadout '${profileToDelete}' deleted`, {
        toastClassName: 'compact-toast'
      })
      // Clear the selected profile after deletion
      store.setSelectedProfile('')
    } else {
      toast.error('Failed to delete profile')
    }
  } catch (error) {
    console.error('Error deleting profile:', error)
    toast.error('Failed to delete profile')
  }
}
</script>

<template>
  <menu-bar :show-stratagems="showStratagems" :show-profiles="showProfiles" :show-user-select="showUserSelect"
    :selected-user="selectedUser" :selected-profile="selectedProfile" :remove-mode="removeMode"
    @toggle-stratagems="store.toggleStratagems()" @toggle-profiles="store.toggleProfiles()"
    @update:selected-user="store.setSelectedUser($event)" @update:selected-profile="store.setSelectedProfile($event)"
    @trigger-remove-mode="triggerRemoveMode" @select-user="store.toggleUserSelect()"
    @overwrite-profile="handleOverwrite" @save-profile="handleSave" @rename-profile="handleRename"
    @delete-profile="handleDelete" class="h-full" />
  <main class="h-full flex items-center justify-center">
    <MainGrid :show-stratagems="showStratagems" :show-profiles="showProfiles" :selected-user="selectedUser"
      :selected-profile="selectedProfile" :remove-mode="removeMode" @select-profile="store.setSelectedProfile($event)"
      @close-profiles="store.closeProfiles()" @removed-macro="startRemoveTimer" />
  </main>
  <Transition name="fade">
    <Modal v-if="showUserSelect" @close="store.toggleUserSelect()">
      <UserSelection @select-user="handleSelectUser" />
    </Modal>
  </Transition>

  <Transition name="fade">
    <Modal v-if="showOverwriteConfirm" @close="showOverwriteConfirm = false">
      <ModalConfirm :action="`overwrite ${selectedProfile}`" @close="showOverwriteConfirm = false"
        @confirm="confirmOverwrite" />
    </Modal>
  </Transition>

  <Transition name="fade">
    <Modal v-if="showSavePrompt" @close="showSavePrompt = false">
      <ModalConfirmInput action="Save new loadout" placeholder="Enter loadout name" @close="showSavePrompt = false"
        @confirm="confirmSave" />
    </Modal>
  </Transition>

  <Transition name="fade">
    <Modal v-if="showRenamePrompt" @close="showRenamePrompt = false">
      <ModalConfirmInput action="Rename loadout" placeholder="Enter new name" @close="showRenamePrompt = false"
        @confirm="confirmRename" />
    </Modal>
  </Transition>

  <Transition name="fade">
    <Modal v-if="showDeleteConfirm" @close="showDeleteConfirm = false">
      <ModalConfirm :action="`delete ${selectedProfile}`" @close="showDeleteConfirm = false" @confirm="confirmDelete" />
    </Modal>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>