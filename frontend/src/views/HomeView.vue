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
    const response = await axios.post('http://localhost:8000/shorten', {
      original_url: originalUrl.value
    })
    shortUrl.value = `${window.location.origin}/${response.data.short_id}` // Assuming redirect is handled by backend or frontend proxy. 
    // Actually, backend handles redirect at /{short_id}. So we should point to backend URL or frontend if we proxy.
    // For now, let's point to backend: http://localhost:8000/{short_id}
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
  <div class="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-center text-gray-800">Shorten Your Link</h2>
    
    <form @submit.prevent="shortenUrl" class="space-y-4">
      <div>
        <label for="url" class="block text-sm font-medium text-gray-700">Enter a long URL</label>
        <input 
          v-model="originalUrl" 
          type="url" 
          id="url" 
          required
          placeholder="https://example.com/very/long/url"
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>
      
      <button 
        type="submit" 
        :disabled="loading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
      >
        {{ loading ? 'Shortening...' : 'Shorten URL' }}
      </button>
    </form>
    
    <div v-if="error" class="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
      {{ error }}
    </div>
    
    <div v-if="shortUrl" class="mt-6 p-4 bg-green-50 border border-green-200 rounded-md text-center">
      <p class="text-sm text-green-600 mb-1">Your shortened URL:</p>
      <a :href="shortUrl" target="_blank" class="text-xl font-bold text-indigo-600 hover:underline break-all">
        {{ shortUrl }}
      </a>
      <div class="mt-2">
         <router-link :to="{ name: 'stats', params: { shortId: shortUrl.split('/').pop() } }" class="text-sm text-gray-500 hover:text-gray-700 underline">
            View Stats
         </router-link>
      </div>
    </div>
  </div>
</template>
