<script setup lang="ts">
import { ChevronLeftIcon, ChevronRightIcon, ZoomInIcon, ZoomOutIcon, FullscreenIcon } from "lucide-vue-next";
import { Button } from "@/components/ui/button";
import { useZoom, ZoomMode } from '@embedpdf/plugin-zoom/vue';
import { useScroll } from "@embedpdf/plugin-scroll/vue";
 
// The composable provides reactive state and methods
const { provides: zoomProvides, state: zoomState } = useZoom();

// Provide scroll functionality
const { provides: scrollProvides, state: scrollState } = useScroll();
</script>
 
<template>
  <div v-if="zoomProvides && scrollProvides" class="relative w-full bottom-12 flex  justify-center no-drag">

    <div class='inline-flex w-fit border rounded-md shadow-xs bg-background mr-2'>
      <Button variant="ghost" size="icon" @click="scrollProvides.scrollToPreviousPage()">
        <ChevronLeftIcon class="w-4 h-4"/>
      </Button>
      <span class="w-14 h-9 flex items-center  justify-center text-sm">
        {{scrollState.currentPage}}/{{scrollState.totalPages}}
      </span>
      <Button variant="ghost" size="icon" @click="scrollProvides.scrollToNextPage()">
        <ChevronRightIcon class="w-4 h-4"/>
      </Button>
    </div>
    <div class='inline-flex w-fit border rounded-md shadow-xs bg-background mr-2'>
      <Button variant="ghost" size="icon" @click="zoomProvides.zoomIn()">
        <ZoomInIcon class="w-4 h-4"/>
      </Button>
      <span class="w-14 h-9 flex items-center  justify-center text-sm">
        {{Math.round(zoomState.currentZoomLevel * 100)}}%
      </span>
      <Button variant="ghost" size="icon" @click="zoomProvides.zoomOut()">
        <ZoomOutIcon class="w-4 h-4"/>
      </Button>
    </div>
    <Button variant="outline" size="icon" @click="zoomProvides.requestZoom(ZoomMode.FitPage)">
      <FullscreenIcon class="w-4 h-4" />
    </Button>
    
  </div>
</template>