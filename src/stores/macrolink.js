import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { MACRO_IMAGES, ICON_TO_KEY } from '@/data/macroData'

export const useMacrolinkStore = defineStore('macrolink', () => {
  // Static macros always in positions 1 and 2
  const STATIC_MACROS = [
    { id: 1, icon: 'redeploy', macroKey: 'Reinforce' },
    { id: 2, icon: 'resupply', macroKey: 'Resupply' },
  ]

  // State
  const macros = ref([...STATIC_MACROS])
  const showStratagems = ref(false)
  const showProfiles = ref(false)
  const removeMode = ref(false)
  const selectedUser = ref(localStorage.getItem('selectedUser') || '')
  const selectedProfile = ref(localStorage.getItem('selectedProfile') || '')
  const showUserSelect = ref(false)

  // User mapping
  const userMap = {
    green: 'user1',
    blue: 'user2',
  }

  // Watch and persist to localStorage
  watch(selectedUser, (newValue) => {
    if (newValue) {
      localStorage.setItem('selectedUser', newValue)
    }
    // Clear profile and reset to static macros when user changes
    selectedProfile.value = ''
    macros.value = [...STATIC_MACROS]
  })

  watch(selectedProfile, (newValue) => {
    if (newValue) {
      localStorage.setItem('selectedProfile', newValue)
    } else {
      localStorage.removeItem('selectedProfile')
    }
  })

  // Actions
  function addMacro(stratagem) {
    const iconName = stratagem.image.replace('.webp', '')
    const existingIndex = macros.value.findIndex((macro) => macro.icon === iconName)

    if (existingIndex !== -1) {
      // Remove if already exists (toggle off)
      macros.value.splice(existingIndex, 1)
    } else {
      // Check if at limit
      if (macros.value.length >= 10) {
        return { error: 'Maximum 10 macros allowed' }
      }

      // Add if not exists
      const nextId =
        macros.value.length > 0 ? Math.max(...macros.value.map((macro) => macro.id)) + 1 : 3

      // Get the macro key from icon name
      const macroKey = ICON_TO_KEY[iconName] || iconName

      macros.value.push({ id: nextId, icon: iconName, macroKey: macroKey })
    }
    return { success: true }
  }

  function removeMacro(macro) {
    // Prevent removing static slots
    if (macro.id === 1 || macro.id === 2) {
      return { error: 'Cannot remove Reinforce or Resupply' }
    }

    const idx = macros.value.findIndex((m) => m.id === macro.id)
    if (idx !== -1) {
      macros.value.splice(idx, 1)
      return { success: true }
    }
    return { error: 'Macro not found' }
  }

  async function loadProfile(user, profile) {
    try {
      const response = await fetch('/all_profiles')
      const allProfilesData = await response.json()

      const jsonKey = userMap[user] || user
      const profileMacros = allProfilesData[jsonKey]?.[profile]

      if (profileMacros && Array.isArray(profileMacros)) {
        // Filter out Reinforce and Resupply (already in static slots)
        const filteredMacros = profileMacros.filter(
          (macroKey) => macroKey !== 'Reinforce' && macroKey !== 'Resupply',
        )

        // Convert to icon format, starting from id 3
        const dynamicMacros = filteredMacros.map((macroKey, index) => {
          const imageFile = MACRO_IMAGES[macroKey]
          const iconName = imageFile ? imageFile.replace('.webp', '') : macroKey.toLowerCase()

          return {
            id: index + 3,
            icon: iconName,
            macroKey: macroKey,
          }
        })

        // Combine static (1-2) + dynamic (3-10), max 8 dynamic
        macros.value = [...STATIC_MACROS, ...dynamicMacros.slice(0, 8)]
      }
    } catch (error) {
      console.error('Failed to load profile:', error)
      return { error: 'Failed to load profile' }
    }
  }

  function toggleStratagems() {
    showStratagems.value = !showStratagems.value
    // Close profiles when opening stratagems
    if (showStratagems.value) {
      showProfiles.value = false
    }
  }

  function toggleProfiles() {
    showProfiles.value = !showProfiles.value
    // Close stratagems when opening profiles
    if (showProfiles.value) {
      showStratagems.value = false
    }
  }

  function toggleUserSelect() {
    showUserSelect.value = !showUserSelect.value
  }

  function closeProfiles() {
    showProfiles.value = false
  }

  function setRemoveMode() {
    removeMode.value = !removeMode.value

    // Close stratagems and profiles when entering remove mode
    if (removeMode.value) {
      showStratagems.value = false
      showProfiles.value = false
    }
  }

  function setSelectedUser(user) {
    selectedUser.value = user
  }

  function setSelectedProfile(profile) {
    selectedProfile.value = profile
  }

  return {
    // State
    macros,
    showStratagems,
    showProfiles,
    removeMode,
    selectedUser,
    selectedProfile,
    showUserSelect,
    // Actions
    addMacro,
    removeMacro,
    loadProfile,
    toggleStratagems,
    toggleProfiles,
    toggleUserSelect,
    closeProfiles,
    setRemoveMode,
    setSelectedUser,
    setSelectedProfile,
  }
})
