<script setup lang="ts">
import {
  SidebarInset,
  SidebarProvider
} from "@/components/ui/sidebar";
import SideNavigate from '@/components/side/SideNavigate.vue';

</script>

<template>
  <SidebarProvider class="w-screen">
    <SideNavigate />
    <SidebarInset class="h-screen">
      <RouterView />
    </SidebarInset>
  </SidebarProvider>

</template>