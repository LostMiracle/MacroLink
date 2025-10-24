<script setup>
import { watch } from 'vue'
import { useToast } from 'vue-toastification'
import MacroButton from './MacroButton.vue'
import Stratagems from './Stratagems.vue'
import Profiles from './Profiles.vue'
import { DYNAMIC_MACROS } from '@/data/macroData'
import { useMacrolinkStore } from '@/stores/macrolink'
import { storeToRefs } from 'pinia'

const toast = useToast()
const store = useMacrolinkStore()

// Get reactive refs from store
const { macros, showStratagems, showProfiles, selectedUser, selectedProfile, removeMode } = storeToRefs(store)

const props = defineProps({
  showStratagems: {
    type: Boolean,
    required: true,
  },
  showProfiles: {
    type: Boolean,
    required: true,
  },
  removeMode: {
    type: Boolean,
    required: false,
    default: false
  },
  selectedUser: {
    type: String,
    required: false,
    default: ''
  },
  selectedProfile: {
    type: String,
    required: false,
    default: ''
  }
})

const emit = defineEmits(['select-profile', 'close-profiles', 'removed-macro'])

// Watch for profile changes and load from store
watch(() => [selectedUser.value, selectedProfile.value], ([user, profile]) => {
  if (user && profile) {
    store.loadProfile(user, profile)
  }
}, { immediate: true })

const addMacro = (stratagem) => {
  const result = store.addMacro(stratagem)
  if (result.error) {
    toast.error(result.error, {
      toastClassName: 'full-toast',
    })
  }
}

const onRemoveClick = (macro) => {
  const result = store.removeMacro(macro)
  if (result.error) {
    toast.warning(result.error)
  } else if (result.success) {
    emit('removed-macro')
  }
}

// Particle background config
const particlesOptions = {
  background: {
    color: {
      value: 'transparent',
    },
  },
  fpsLimit: 20,
  particles: {
    color: {
      value: '#ffffff',
    },
    links: {
      color: '#fbff00',
      distance: 100,
      enable: true,
      opacity: 0.3,
      width: 1,
    },
    move: {
      enable: true,
      speed: 0.4,
      direction: 'none',
      random: false,
      straight: false,
      outModes: {
        default: 'out',
      },
    },
    number: {
      value: 65,
      density: {
        enable: false,
        area: 800,
      },
    },
    opacity: {
      value: 0.5,
    },
    shape: {
      type: 'circle',
    },
    size: {
      value: { min: 1, max: 2 },
    },
  },
  detectRetina: true,
}

const triggerMacro = async (macro) => {
  const userKey = selectedUser.value === 'green' ? 'user1' : 'user2'

  let macroKey = macro.macroKey
  let displayName = macroKey.replaceAll('_', ' ')

  try {
    const response = await fetch(`/trigger/${macroKey}?user=${userKey}`)
    // Handle response
    toast.success(`Triggered [${displayName}]`)
  } catch (error) {
    toast.error('Failed to trigger macro')
  }
}

const handleMacroClick = (macro) => {
  if (removeMode.value) {
    onRemoveClick(macro)
  } else {
    triggerMacro(macro)
  }
}
</script>

<template>
  <div class="h-full w-full flex items-center justify-center relative bg-container">
    <!-- Particles background -->
    <vue-particles id="tsparticles" :options="particlesOptions" class="absolute inset-0 z-0" />

    <!-- Main grid on top -->
    <div class="grid grid-cols-5 gap-4 mx-auto relative z-10"
      style="grid-template-rows: repeat(2, 1fr); height: 90%; width: auto;">
      <MacroButton v-for="macro in macros" :key="macro.id" :macro="macro" @click="handleMacroClick(macro)" />
    </div>
  </div>

  <Transition name="slide-down">
    <Stratagems v-if="showStratagems" :show-stratagems="showStratagems" :current-macros="macros"
      @select-stratagem="addMacro" />
  </Transition>
  <Transition name="slide-down">
    <Profiles v-if="showProfiles" :show-profiles="showProfiles" :selected-user="selectedUser"
      :selected-profile="selectedProfile"
      @select-profile="(profile) => { emit('select-profile', profile); emit('close-profiles'); }" />
  </Transition>

  <!-- detail text-->
  <div
    class="absolute bottom-0 left-0 right-0 text-center px-2 text-[8px] flex flex-row justify-between text-yellow-300 font-thin opacity-50 z-5">
    <div><router-link to="/dashboard">
        <span class="text-[12px]">> ::</span> REMOTE COMMAND<span class="text-[12px]">:</span> SUPER DESTROYER //
        SIGNAL<span class="text-[12px]">:</span> ALL CLEAR // REQUEST<span class="text-[12px]">:</span> ENGAGE
      </router-link>
    </div>
    <div><span class="text-[12px]">::</span> STRATAGEM ARRAY STANDBY <span class="text-[12px]">::</span> CMD_QUEUE<span
        class="text-[12px]">:</span> IDLE // READY FOR DEPLOYMENT</div>
  </div>
</template>

<style lang="less" scoped>
/* Enter transitions - sliding down from top */
.slide-down {
  &-enter-active {
    transition: all 0.3s ease-out;
  }

  &-leave-active {
    transition: all 0.2s ease-in;
  }

  &-enter-from {
    transform: translateY(-100%);
    opacity: 0;
    border-color: transparent !important;
  }

  &-enter-to {
    transform: translateY(0);
    opacity: 1;
    transition: transform 0.3s ease-out,
      opacity 0.3s ease-out,
      border-color 0.2s 0.3s;
  }

  &-leave-from {
    transform: translateY(0);
    opacity: 1;
  }

  &-leave-to {
    transform: translateY(-100%);
    opacity: 0;
    border-color: transparent !important;
    transition: transform 0.2s ease-in,
      opacity 0.2s ease-in,
      border-color 0s 0.2s;
  }
}

.bg-container {
  position: relative;

  &::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: url('/images/super-earth.webp');
    background-size: 35%;
    background-position: center;
    background-repeat: no-repeat;
    opacity: 0.05;
    /* Adjust 0-1 */
    z-index: -1;
    /* Behind everything */
  }

  // Grid overlay
  &::after {
    content: "";
    position: absolute;
    inset: 0;
    background-image: url('/images/grid-transparent.webp');
    background-size: auto;
    /* Use image's natural size */
    background-position: center;
    background-repeat: repeat;
    opacity: 0.035;
    z-index: -1;
  }
}
</style>