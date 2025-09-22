<script setup lang="ts">
import { SidebarTrigger } from "@/components/ui/sidebar";
import Separator from "@/components/ui/separator/Separator.vue";

defineProps<{
  headerText: string
}>();
</script>

<template>
  <header
    class="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12 border-b">
    <div class="flex items-center gap-2 px-4">
      <SidebarTrigger class="-ml-1" />
      <Separator orientation="vertical" class="mr-2 h-4" />
      <span>{{ headerText }}</span>
    </div>
  </header>

</template>