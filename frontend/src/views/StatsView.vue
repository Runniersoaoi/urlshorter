<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const route = useRoute()
const shortId = route.params.shortId
const stats = ref(null)
const loading = ref(true)
const error = ref('')

const chartData = ref({
  labels: [],
  datasets: [{ data: [] }]
})

const chartOptions = {
  responsive: true
}

onMounted(async () => {
  try {
    const response = await axios.get(`https://shortter-api.matiasaquino.com/stats/${shortId}`)
    stats.value = response.data
    
    // Prepare chart data (e.g., browsers)
    if (stats.value.browsers) {
        chartData.value = {
            labels: Object.keys(stats.value.browsers),
            datasets: [
                {
                    label: 'Clicks por navegador',
                    backgroundColor: '#4f46e5',
                    data: Object.values(stats.value.browsers)
                }
            ]
        }
    }
  } catch (err) {
    error.value = 'Failed to load statistics.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Loading statistics...</p>
    </div>
    
    <div v-else-if="error" class="text-center py-12 text-red-600">
      {{ error }}
    </div>
    
    <div v-else class="space-y-6">
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Métricas de {{ shortId }}</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div class="p-4 bg-indigo-50 rounded-lg">
            <p class="text-sm text-indigo-600 font-medium">Total de clicks</p>
            <p class="text-3xl font-bold text-indigo-900">{{ stats.total_clicks }}</p>
          </div>
          <!-- Add more summary cards here -->
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-lg shadow-md">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Buscadores</h3>
            <div v-if="chartData.labels.length > 0">
                <Bar :data="chartData" :options="chartOptions" />
            </div>
            <div v-else class="text-center py-8 text-gray-500 italic">
                No hay datos de navegación aún.
            </div>
        </div>
        
        <div class="bg-white p-6 rounded-lg shadow-md">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Países</h3>
            <ul class="divide-y divide-gray-200">
                <li v-for="(count, country) in stats.countries" :key="country" class="py-2 flex justify-between">
                    <span class="text-gray-700">{{ country }}</span>
                    <span class="font-medium text-gray-900">{{ count }}</span>
                </li>
                <li v-if="Object.keys(stats.countries).length === 0" class="py-2 text-center text-gray-500 italic">No hay datos de ubicación aún.</li>
            </ul>
        </div>
      </div>
    </div>
  </div>
</template>
