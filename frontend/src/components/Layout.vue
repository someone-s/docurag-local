<script setup lang="ts">
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger
} from "@/components/ui/sidebar"

import SideNavigate from '@/components/side/SideNavigate.vue';
import Query from "@/components/query/Query.vue";

</script>

<template>
  <SidebarProvider class="w-screen">
    <SideNavigate />
    <SidebarInset class="h-screen">
      <header
        class="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12 border-b">
        <div class="flex items-center gap-2 px-4">
          <SidebarTrigger class="-ml-1" />
        </div>
      </header>
      <Query />
    </SidebarInset>
  </SidebarProvider>

</template>