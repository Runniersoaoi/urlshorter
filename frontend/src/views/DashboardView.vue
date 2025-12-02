<template>
  <div class="min-h-screen bg-gray-50 pt-20 pb-10">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col sm:flex-row justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-brand-dark">Mis enlaces</h1>
        <button @click="openCreateModal" class="mt-4 sm:mt-0 bg-brand-orange text-white px-4 py-2 rounded-md font-medium hover:bg-gray-600 transition bg-gray-700 hover:cursor-pointer">
          Crear nuevo enlace
        </button>
      </div>

      <!-- Filters -->
      <div class="bg-white p-4 rounded-lg shadow mb-6 flex flex-col md:flex-row gap-4">
        <div class="grow">
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
          <input v-model="searchQuery" type="text" placeholder="Buscar por título..." class="w-full border-gray-300 rounded-md shadow-sm focus:ring-brand-orange focus:border-brand-orange" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Desde</label>
          <input v-model="startDate" type="date" class="border-gray-300 rounded-md shadow-sm focus:ring-brand-orange focus:border-brand-orange" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Hasta</label>
          <input v-model="endDate" type="date" class="border-gray-300 rounded-md shadow-sm focus:ring-brand-orange focus:border-brand-orange" />
        </div>
      </div>
      
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <ul role="list" class="divide-y divide-gray-200">
          <li v-for="url in filteredUrls" :key="url.short_id">
            <div class="px-4 py-4 sm:px-6 hover:bg-gray-50 transition">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-4 overflow-hidden">
                    <!-- QR Thumbnail -->
                    <img :src="`http://localhost:8000/qr/${url.short_id}`" alt="QR" class="w-12 h-12 border rounded p-1 bg-white flex-shrink-0 cursor-pointer" @click="downloadQr(url.short_id)" title="Click to Download" />
                    
                    <div class="truncate">
                        <p class="text-lg font-semibold text-brand-dark truncate">{{ url.title || url.short_id }}</p>
                        <div class="flex items-center gap-2 text-sm text-brand-orange">
                            <a :href="`http://localhost:8000/${url.short_id}`" target="_blank" class="hover:underline truncate">
                                http://localhost:8000/{{ url.short_id }}
                            </a>
                            <button @click="copyToClipboard(`http://localhost:8000/${url.short_id}`)" class="text-gray-400 hover:text-gray-600" title="Copiar">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                            </button>
                            <button @click="downloadQr(url.short_id)" class="text-gray-400 hover:text-gray-600" title="Descargar QR">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="flex items-center gap-2">
                  <router-link :to="`/stats/${url.short_id}`" class="text-gray-400 hover:text-brand-dark" title="Estadísticas">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </router-link>
                  <button @click="openEditModal(url)" class="text-gray-400 hover:text-blue-600" title="Editar">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="deleteUrl(url)" class="text-gray-400 hover:text-red-600" title="Eliminar">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              <div class="mt-2 text-sm text-gray-500 truncate">
                {{ url.original_url }}
              </div>
              <div class="mt-1 text-xs text-gray-400">
                Creado: {{ new Date(url.created_at).toLocaleDateString() }}
              </div>
            </div>
          </li>
          <li v-if="filteredUrls.length === 0" class="px-4 py-8 text-center text-gray-500">
              No se encontraron enlaces.
          </li>
        </ul>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg max-w-md w-full p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Crear nuevo enlace</h3>
            <form @submit.prevent="createUrl">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700">URL Original</label>
                    <input v-model="newUrl.original_url" type="url" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-brand-orange focus:border-brand-orange" />
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700">Título (Opcional)</label>
                    <input v-model="newUrl.title" type="text" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-brand-orange focus:border-brand-orange" />
                </div>
                <div class="flex justify-end gap-3">
                    <button type="button" @click="showCreateModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200">Cancelar</button>
                    <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-brand-orange rounded-md hover:bg-gray-700 hover:cursor-pointer transition hover:duration-150 bg-gray-700">Crear</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg max-w-md w-full p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Editar enlace</h3>
            <form @submit.prevent="updateUrl">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700">Título</label>
                    <input v-model="currentUrl.title" type="text" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-brand-orange focus:border-brand-orange" />
                </div>
                <div class="flex justify-end gap-3">
                    <button type="button" @click="showEditModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200">Cancelar</button>
                    <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-brand-orange rounded-md hover:bg-gray-700 bg-gray-700 hover:cursor-pointer">Guardar</button>
                </div>
            </form>
        </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const urls = ref([])
const router = useRouter()
const searchQuery = ref('')
const startDate = ref('')
const endDate = ref('')

const showCreateModal = ref(false)
const showEditModal = ref(false)
const newUrl = ref({ original_url: '', title: '' })
const currentUrl = ref({})

const filteredUrls = computed(() => {
    return urls.value.filter(url => {
        const matchesSearch = (url.title || '').toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                              url.short_id.includes(searchQuery.value)
        
        let matchesDate = true
        if (startDate.value) {
            matchesDate = matchesDate && new Date(url.created_at) >= new Date(startDate.value)
        }
        if (endDate.value) {
            // End date should be inclusive, so set to end of day
            const end = new Date(endDate.value)
            end.setHours(23, 59, 59, 999)
            matchesDate = matchesDate && new Date(url.created_at) <= end
        }
        
        return matchesSearch && matchesDate
    })
})

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

const fetchUrls = async () => {
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
}

const openCreateModal = () => {
    newUrl.value = { original_url: '', title: '' }
    showCreateModal.value = true
}

const createUrl = async () => {
    const token = localStorage.getItem('token')
    try {
        await axios.post('http://localhost:8000/shorten', newUrl.value, {
            headers: { Authorization: `Bearer ${token}` }
        })
        showCreateModal.value = false
        await fetchUrls()
    } catch (e) {
        alert('Error creating URL')
    }
}

const openEditModal = (url) => {
    currentUrl.value = { ...url }
    showEditModal.value = true
}

const updateUrl = async () => {
    const token = localStorage.getItem('token')
    try {
        await axios.put(`http://localhost:8000/urls/${currentUrl.value.short_id}`, {
            title: currentUrl.value.title
        }, {
            headers: { Authorization: `Bearer ${token}` }
        })
        showEditModal.value = false
        await fetchUrls()
    } catch (e) {
        alert('Error updating URL')
    }
}

const deleteUrl = async (url) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este enlace?')) return
    
    const token = localStorage.getItem('token')
    try {
        await axios.delete(`http://localhost:8000/urls/${url.short_id}`, {
            headers: { Authorization: `Bearer ${token}` }
        })
        await fetchUrls()
    } catch (e) {
        alert('Error deleting URL')
    }
}

onMounted(fetchUrls)
</script>
