<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'
import {
  SidebarProvider,
  SidebarTrigger
} from "@/components/ui/sidebar"

import PDFViewer from '@/components/pdf/PDFViewer.vue';
import type { PDFDocument } from '@/components/pdf/PDFDocument';
import axios from 'axios';
import Navigate from './navigate/Navigate.vue';

let documents: PDFDocument[] = [];

async function fetchAllDocuments(outDocuments: PDFDocument[]) {
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
    outDocuments.push({
      name: `document-${id}.pdf`,
      id: id,
      file: listResponse.data
    });
  }
};
fetchAllDocuments(documents);
</script>

<template>
  <SidebarProvider class="w-screen">
    <Navigate />
    <main class="w-screen">
      <SidebarTrigger class="absolute"/>
      <slot>
        <ResizablePanelGroup direction="horizontal">
          <ResizablePanel class="h-screen">
          </ResizablePanel>
          <ResizableHandle with-handle />
          <ResizablePanel class="">
            <PDFViewer class="h-full" :documents="documents" />
          </ResizablePanel>
        </ResizablePanelGroup>
      </slot>
    </main>
  </SidebarProvider>

</template>