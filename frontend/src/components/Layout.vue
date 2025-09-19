<script setup lang="ts">
import {
  SidebarProvider,
  SidebarTrigger
} from "@/components/ui/sidebar"

import SideNavigate from '@/components/side/SideNavigate.vue';
import Query from "@/components/query/Query.vue";

</script>

<template>
  <SidebarProvider class="w-screen">
    <SideNavigate />
    <main class="w-screen">
      <SidebarTrigger class="absolute z-10" />
      <slot>
        <Query />
      </slot>
    </main>
  </SidebarProvider>

</template>