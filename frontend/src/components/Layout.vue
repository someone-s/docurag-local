<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'
import PDFViewer from '@/components/pdf/PDFViewer.vue';
import type { PDFDocument } from '@/components/pdf/PDFDocument';
import axios from 'axios';

let documents: PDFDocument[] = [];

(async () => {
  const listResponse = await axios.get('http://0.0.0.0:8081/document/list');

  const ids = listResponse.data.ids as number[];
  for (const id of ids) {
    const listResponse = await axios.get(`http://0.0.0.0:8081/document/fetch/${id}`,
      {
        responseType: 'arraybuffer',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/pdf'
        }
      });
    documents.push({
      name: `document-${id}.pdf`,
      id: id,
      file: listResponse.data
    });
  }
})()

</script>

<template>
  <ResizablePanelGroup direction="horizontal">
    <ResizablePanel class="h-screen">
    </ResizablePanel>
    <ResizableHandle with-handle />
    <ResizablePanel class="">
      <PDFViewer class="h-full" :documents="documents" />
    </ResizablePanel>
  </ResizablePanelGroup>
</template>