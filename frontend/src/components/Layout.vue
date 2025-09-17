<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'
import PDFViewer from '@/components/ui/pdf/PDFViewer.vue';
import type { PDFDocument } from '@/components/ui/pdf/PDFDocument';

let documents: PDFDocument[] = []
</script>

<template>
  <ResizablePanelGroup direction="horizontal">
    <ResizablePanel class="h-screen">
      
      <PDFViewer class="h-full" :documents="documents"/>
    </ResizablePanel>
    <ResizableHandle with-handle />
    <ResizablePanel>Two</ResizablePanel>
  </ResizablePanelGroup>
</template>