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

import Viewer from '@/components/pdf/Viewer.vue';
import type { PDFDocument } from '@/components/pdf/document';
import axios from 'axios';
import Navigate from './side/Navigate.vue';

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
          <ResizablePanel>
            <Viewer class="h-full" :documents="documents" />
          </ResizablePanel>
        </ResizablePanelGroup>
      </slot>
    </main>
  </SidebarProvider>

</template>