<template>
  <div class="min-h-screen bg-gray-50 pt-20">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold text-brand-dark mb-8">My Links</h1>
      
      <div class="bg-white shadow overflow-hidden sm:rounded-md">
        <ul role="list" class="divide-y divide-gray-200">
          <li v-for="url in urls" :key="url.short_id">
            <div class="px-4 py-4 sm:px-6">
              <div class="flex items-center justify-between">
                <div class="text-sm font-medium text-brand-orange truncate">
                  <a :href="`http://localhost:8000/${url.short_id}`" target="_blank" class="hover:underline">
                    http://localhost:8000/{{ url.short_id }}
                  </a>
                </div>
                <div class="ml-2 flex-shrink-0 flex">
                  <router-link :to="`/stats/${url.short_id}`" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 hover:bg-green-200">
                    View Stats
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
                    Created on {{ new Date(url.created_at).toLocaleDateString() }}
                  </p>
                </div>
              </div>
            </div>
          </li>
          <li v-if="urls.length === 0" class="px-4 py-4 sm:px-6 text-center text-gray-500">
              You haven't created any links yet.
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
