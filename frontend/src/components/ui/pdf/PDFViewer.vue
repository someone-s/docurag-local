<script setup lang="ts">
import { usePdfiumEngine } from '@embedpdf/engines/vue';
import { EmbedPDF } from '@embedpdf/core/vue';
import { createPluginRegistration } from '@embedpdf/core';
import type { PdfFile } from '@embedpdf/models';
 
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

function onchange(id: number) {

  let document = props.documents.find(document => document.id == id)
  if (document == null) return

  let pdfFile: PdfFile = { id: `${id}`, content: document.file }
  engine.value?.openDocumentBuffer(pdfFile) // Can specify password in optional open options
}
</script>
 
<template>
  <div class="relative">
    <div v-if="isLoading || !engine" class="loading-pane">
      Loading PDF Engine...
    </div>
    
    <EmbedPDF v-else :engine="engine" :plugins="plugins">
      <Viewport class="viewport-class no-scrollbar bg-background">
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
      <PDFSelect :documents="props.documents" v-on:change="onchange"></PDFSelect>
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