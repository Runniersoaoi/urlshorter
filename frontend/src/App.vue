<script setup>
import { RouterView, useRouter } from "vue-router";
import { ref, onMounted } from "vue";

const router = useRouter();
const isLoggedIn = ref(false);

onMounted(() => {
  checkLoginStatus();
});

const checkLoginStatus = () => {
  isLoggedIn.value = !!localStorage.getItem("token");
};

const logout = () => {
  localStorage.removeItem("token");
  isLoggedIn.value = false;
  router.push("/");
};

// Watch for route changes to update auth status
router.afterEach(() => {
  checkLoginStatus();
});
</script>

<template>
  <div class="min-h-screen bg-white font-sans">
    <header class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <router-link to="/" class="text-2xl font-bold text-brand-orange">
                Shorter
              </router-link>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <template v-if="!isLoggedIn">
              <router-link
                to="/login"
                class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 hover:cursor-pointer transition hover:duration-150"
              >
                Iniciar sesión
              </router-link>
              <router-link
                to="/register"
                class="bg-brand-dark text-gray-700 hover:bg-blue-900 px-4 py-2 rounded-md text-sm font-medium hover:cursor-pointer transition hover:duration-150 hover:text-white"
              >
                Registrarse
              </router-link>
            </template>
            <template v-else>
              <router-link
                to="/dashboard"
                class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 hover:cursor-pointer transition hover:duration-150"
              >
                Dashboard
              </router-link>
              <button
                @click="logout"
                class="text-gray-700  px-3 py-2 rounded-md text-sm font-medium hover:bg-red-500 hover:text-white  hover:cursor-pointer transition hover:duration-150"
              >
                Cerrar sesión
              </button>
            </template>
          </div>
        </div>
      </div>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>
