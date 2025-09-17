<script setup lang="ts">
import { usePdfiumEngine } from '@embedpdf/engines/vue';
import { EmbedPDF } from '@embedpdf/core/vue';
import { createPluginRegistration } from '@embedpdf/core';
 
// Import the essential plugins and their components
import { ViewportPluginPackage, Viewport } from '@embedpdf/plugin-viewport/vue';
import { Scroller, ScrollPluginPackage } from '@embedpdf/plugin-scroll/vue';
import { LoaderPluginPackage } from '@embedpdf/plugin-loader/vue';
import { RenderLayer, RenderPluginPackage } from '@embedpdf/plugin-render/vue';

// Import zoom functionality
import { ZoomMode, ZoomPluginPackage } from '@embedpdf/plugin-zoom/vue';
import PDFControl from './PDFControl.vue';
import PDFSelect from './PDFSelect.vue';
import type { PDFDocument } from './PDFDocument';
import { ref } from 'vue';

const componentKey = ref(0);
 
// 1. Initialize the engine with the Vue composable
const { engine, isLoading } = usePdfiumEngine();
 
// 2. Register the plugins you need
const plugins = [
  createPluginRegistration(LoaderPluginPackage),
  createPluginRegistration(ViewportPluginPackage),
  createPluginRegistration(ScrollPluginPackage),
  createPluginRegistration(RenderPluginPackage),
  createPluginRegistration(ZoomPluginPackage, {
    // Set the initial zoom level when a document loads
    defaultZoomLevel: ZoomMode.FitPage,
  }),
];


const props = defineProps<{
  documents: PDFDocument[]
}>();
</script>
 
<template>
  <div class="relative">
    <div v-if="isLoading || !engine" class="loading-pane">
      Loading PDF Engine...
    </div>
    
    <EmbedPDF v-else :engine="engine" :plugins="plugins">
      <Viewport class="viewport-class no-scrollbar bg-background" :key="componentKey">
        <Scroller>
          <template #default="{ page }">
            <div
              :style="{
                width: `${page.width}px`,
                height: `${page.height}px`,
              }"
            >
              <RenderLayer :pageIndex="page.pageIndex" />
            </div>
          </template>
        </Scroller>
      </Viewport>
      <PDFSelect :documents="props.documents" :reload="() => componentKey++"></PDFSelect>
      <PDFControl></PDFControl>
    </EmbedPDF>
  </div>
</template>
 
<style scoped>
.loading-pane {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>