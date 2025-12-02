<template>
  <div class="min-h-screen bg-gray-50 pt-20">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold text-brand-dark mb-8">Mis enlaces</h1>
      
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <ul role="list" class="divide-y divide-gray-200">
          <li v-for="url in urls" :key="url.short_id">
            <div class="px-4 py-4 sm:px-6">
              <div class="flex items-center justify-between">
                <div class="text-sm font-medium text-brand-orange truncate flex items-center gap-2">
                  <a :href="`http://localhost:8000/${url.short_id}`" target="_blank" class="hover:underline">
                    http://localhost:8000/{{ url.short_id }}
                  </a>
                  <button @click="copyToClipboard(`http://localhost:8000/${url.short_id}`)" class="text-gray-400 hover:text-gray-600" title="Copy Link">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                  <button @click="downloadQr(url.short_id)" class="text-gray-400 hover:text-gray-600" title="Download QR">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4h-4v-4H8m13-9a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5z" />
                    </svg>
                  </button>
                </div>
                <div class="ml-2 flex-shrink-0 flex">
                  <router-link :to="`/stats/${url.short_id}`" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 hover:bg-green-200">
                    Ver estadísticas
                  </router-link>
                </div>
              </div>
              <div class="mt-2 sm:flex sm:justify-between">
                <div class="sm:flex">
                  <p class="flex items-center text-sm text-gray-500 truncate">
                    {{ url.original_url }}
                  </p>
                </div>
                <div class="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                  <p>
                    Creación: {{ new Date(url.created_at).toLocaleDateString() }}
                  </p>
                </div>
              </div>
            </div>
          </li>
          <li v-if="urls.length === 0" class="px-4 py-4 sm:px-6 text-center text-gray-500">
              Aún no has creado ningún enlace.
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const urls = ref([])
const router = useRouter()

const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text)
        alert('Link copied!')
    } catch (err) {
        console.error('Failed to copy: ', err)
    }
}

const downloadQr = async (shortId) => {
    const response = await axios.get(`http://localhost:8000/qr/${shortId}`, { responseType: 'blob' })
    const blob = new Blob([response.data], { type: 'image/png' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `qr-${shortId}.png`
    link.click()
    URL.revokeObjectURL(link.href)
}

onMounted(async () => {
    const token = localStorage.getItem('token')
    if (!token) {
        router.push('/login')
        return
    }

    try {
        const response = await axios.get('http://localhost:8000/users/me/urls', {
            headers: { Authorization: `Bearer ${token}` }
        })
        urls.value = response.data
    } catch (e) {
        if (e.response?.status === 401) {
            localStorage.removeItem('token')
            router.push('/login')
        }
    }
})
</script>
