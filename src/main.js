import './assets/main.css'
import './assets/main.less'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

import App from './App.vue'
import router from './router'

import Particles from '@tsparticles/vue3'
import { loadSlim } from '@tsparticles/slim'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(toast, {
  position: 'bottom-center',
  timeout: 5000,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false,
})

app.use(Particles, {
  init: async (engine) => {
    await loadSlim(engine)
  },
})

app.mount('#app')
