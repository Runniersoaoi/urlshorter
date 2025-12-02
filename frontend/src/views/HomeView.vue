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
</script>

<template>
  <div class="bg-brand-dark min-h-[calc(100vh-64px)] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl w-full text-center space-y-8">
      <div>
        <h2 class="text-brand-orange text-sm font-bold tracking-wide uppercase">Bitly Links</h2>
        <h1 class="mt-2 text-4xl font-extrabold text-white sm:text-5xl sm:tracking-tight lg:text-6xl">
          Crea enlaces de alto rendimiento<br/>con nuestro acortador de URL
        </h1>
        <p class="mt-4 max-w-2xl mx-auto text-xl text-gray-300">
          Crea relaciones duraderas con tu público utilizando links acortados, fiables y rastreables con la Bitly Connections Platform.
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
            class="inline-flex items-center justify-center px-8 py-4 border border-transparent text-base font-medium rounded-md text-brand-dark bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-orange sm:w-auto border-l sm:border-l-gray-200 font-bold"
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
        <div class="flex items-center justify-center gap-4">
            <a :href="shortUrl" target="_blank" class="text-2xl font-bold text-brand-orange hover:underline break-all">
                {{ shortUrl }}
            </a>
            <button @click="navigator.clipboard.writeText(shortUrl)" class="text-sm text-gray-400 hover:text-gray-600">
                (Copiar)
            </button>
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
