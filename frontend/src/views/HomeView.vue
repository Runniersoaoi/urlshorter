<script setup>
import { ref } from 'vue'
import axios from 'axios'

const originalUrl = ref('')
const shortUrl = ref('')
const error = ref('')
const loading = ref(false)

const shortenUrl = async () => {
  loading.value = true
  error.value = ''
  shortUrl.value = ''
  
  try {
    const token = localStorage.getItem('token')
    const headers = token ? { Authorization: `Bearer ${token}` } : {}
    
    const response = await axios.post('http://localhost:8000/shorten', {
      original_url: originalUrl.value
    }, { headers })
    
    shortUrl.value = `http://localhost:8000/${response.data.short_id}`
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail
    } else {
      error.value = 'An error occurred. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text)
        alert('Link copied to clipboard!')
    } catch (err) {
        console.error('Failed to copy: ', err)
    }
}

const downloadQr = async (url) => {
    const shortId = url.split('/').pop()
    const response = await axios.get(`http://localhost:8000/qr/${shortId}`, { responseType: 'blob' })
    const blob = new Blob([response.data], { type: 'image/png' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `qr-${shortId}.png`
    link.click()
    URL.revokeObjectURL(link.href)
}
</script>

<template>
  <div class="bg-brand-dark min-h-[calc(100vh-64px)] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl w-full text-center space-y-8">
      <div>
        <h2 class="text-brand-orange text-sm font-bold tracking-wide uppercase">Shorter Links</h2>
        <h1 class="mt-2 text-4xl font-extrabold text-black sm:text-5xl sm:tracking-tight lg:text-6xl">
          Crea tu enlace corto <br/>con nuestro acortador de URL
        </h1>
        <p class="mt-4 max-w-2xl mx-auto text-xl text-gray-800">
          Crea enlaces que puedes compartir con tu público, fiables y rastreables con Shorter.
        </p>
      </div>

      <div class="mt-10 max-w-3xl mx-auto">
        <form @submit.prevent="shortenUrl" class="bg-white p-2 rounded-lg shadow-lg flex flex-col sm:flex-row gap-2">
          <div class="flex-grow">
            <label for="url" class="sr-only">Enter a long URL</label>
            <input 
              v-model="originalUrl" 
              type="url" 
              id="url" 
              required
              placeholder="Introduce tu URL larga aquí..."
              class="block w-full px-4 py-4 text-base text-gray-900 placeholder-gray-500 border-0 focus:ring-0 rounded-md"
            />
          </div>
          <button 
            type="submit" 
            :disabled="loading"
            class="inline-flex items-center justify-center px-8 py-4 border border-transparent text-base font-medium rounded-md text-brand-dark bg-white hover:bg-gray-200 hover:cursor-pointer transition hover:duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-orange sm:w-auto border-l sm:border-l-gray-200 font-bold"
          >
            {{ loading ? 'Acortando...' : 'Acortar link' }}
          </button>
        </form>
      </div>
      
      <div v-if="error" class="mt-4 p-4 bg-red-500 text-white rounded-md max-w-3xl mx-auto">
        {{ error }}
      </div>
      
      <div v-if="shortUrl" class="mt-6 p-6 bg-white rounded-lg shadow-xl max-w-3xl mx-auto text-center">
        <p class="text-sm text-gray-500 mb-2">Tu enlace acortado:</p>
        <div class="flex flex-col items-center justify-center gap-4">
            <div class="flex items-center gap-4">
                <a :href="shortUrl" target="_blank" class="text-2xl font-bold text-brand-orange hover:underline break-all">
                    {{ shortUrl }}
                </a>
                <button @click="copyToClipboard(shortUrl)" class="text-sm text-gray-400 hover:text-gray-600 hover:cursor-pointer">
                    (Copiar)
                </button>
            </div>
            
            <div class="mt-4 flex flex-col items-center hover:cursor-pointer">
                <img :src="`http://localhost:8000/qr/${shortUrl.split('/').pop()}`" alt="QR Code" class="w-32 h-32 border p-1 rounded" />
                <button @click="downloadQr(shortUrl)" class="mt-2 text-xs text-brand-dark hover:underline hover:cursor-pointer">
                    Descargar QR
                </button>
            </div>
        </div>
        <div class="mt-4">
           <router-link :to="{ name: 'stats', params: { shortId: shortUrl.split('/').pop() } }" class="text-brand-dark hover:text-brand-orange font-medium underline">
              Ver estadísticas
           </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
