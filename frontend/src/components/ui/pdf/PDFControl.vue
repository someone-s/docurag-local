<script setup lang="ts">
import { ChevronLeftIcon, ChevronRightIcon, ZoomInIcon, ZoomOutIcon, HandGrabIcon, HandIcon } from "lucide-vue-next";
import { Button } from "@/components/ui/button";
import { Toggle } from "@/components/ui/toggle";
import { useZoom } from '@embedpdf/plugin-zoom/vue';
import { useScroll } from "@embedpdf/plugin-scroll/vue";
import { usePan } from "@embedpdf/plugin-pan/vue";
 
// The composable provides reactive state and methods
const { provides: zoomProvides, state: zoomState } = useZoom();

// Provide scroll functionality
const { provides: scrollProvides, state: scrollState } = useScroll();

// Provide pan functionality
const { provides: panProvides, isPanning } = usePan()
</script>
 
<template>
  <div v-if="zoomProvides && scrollProvides && panProvides" class="relative w-full bottom-12 flex  justify-center">

    <div class='inline-flex w-fit border rounded-md shadow-xs bg-background mr-2'>
      <Button variant="ghost" size="icon" @click="scrollProvides.scrollToPreviousPage()">
        <ChevronLeftIcon class="w-4 h-4"/>
      </Button>
      <span class="w-14 h-9 flex items-center  justify-center">
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
      <span class="w-14 h-9 flex items-center  justify-center">
        {{Math.round(zoomState.currentZoomLevel * 100)}}%
      </span>
      <Button variant="ghost" size="icon" @click="zoomProvides.zoomOut()">
        <ZoomOutIcon class="w-4 h-4"/>
      </Button>
    </div>
    <Toggle variant="outline" class="bg-background" :model-value="isPanning" v-on:update:model-value="(state) => { if (state) panProvides?.enablePan(); else panProvides?.disablePan(); }">
      <HandGrabIcon v-if="isPanning" class="w-4 h-4" />
      <HandIcon v-else class="w-4 h-4" />
    </Toggle>
    
  </div>
</template>