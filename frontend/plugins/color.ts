import Vue from 'vue'

declare module 'vue/types/vue' {
  interface Vue {
    $contrastColor(hexString: string): string
    $generateColor(str: string): string
  }
}

Vue.prototype.$generateColor = (str: string) => {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  let color = '#'
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xFF
    color += ('00' + value.toString(16)).substr(-2)
  }
  return color
}

Vue.prototype.$contrastColor = (hexString: string) => {
  const r = parseInt(hexString.substr(1, 2), 16)
  const g = parseInt(hexString.substr(3, 2), 16)
  const b = parseInt(hexString.substr(5, 2), 16)
  return (r * 299 + g * 587 + b * 114) / 1000 < 128 ? '#ffffff' : '#000000'
}