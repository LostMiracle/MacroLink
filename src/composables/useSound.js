export function useSound(soundFile) {
  const play = () => {
    const audio = new Audio(`/sounds/${soundFile}`)
    audio.volume = 0.5 // adjust 0-1
    audio.play().catch((err) => console.warn('Sound play failed:', err))
  }

  return { play }
}
