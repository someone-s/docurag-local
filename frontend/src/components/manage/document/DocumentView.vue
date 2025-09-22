<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'
import LayoutHeader from '@/components/layout/LayoutHeader.vue';
import type { PDFDocument } from '@/components/pdf/pdf-types';
import axios from 'axios';
import PDFViewer from '@/components/pdf/PDFViewer.vue';
import DocumentTable from './DocumentTable.vue';
import { columns, type Payment } from './document-types';
import { onMounted, ref } from 'vue';

const documents: PDFDocument[] = [];

async function fetchDocument(id: number, name: string) {
  navigator.locks.request('fetchDocument', async (_) => {
    if (!Number.isInteger(id)) return;

    if (documents.some(document => document.id == id)) return;


    const listResponse = await axios.get(`http://0.0.0.0:8081/document/fetch/${id}`,
      {
        responseType: 'arraybuffer',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/pdf'
        }
      });
    documents.push({
      name: name,
      id: id,
      file: listResponse.data
    });
  });
}


const data = ref<Payment[]>([])

async function getData(): Promise<Payment[]> {

  return [... Array(100).keys()]
  .map((_, id) => {
    return {      
      id: `${id}`,
      amount: 100,
      status: 'pending',
      email: `${id}@example.comaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`,
    }
  })
}

onMounted(async () => {
  data.value = await getData()
})

</script>

<template>
  <LayoutHeader header-text="Document" />
  <ResizablePanelGroup direction="horizontal" class="h-full" auto-save-id="document-group">
    <ResizablePanel :min-size="40">
      <div class="m-2 h-full">
        <DocumentTable :columns="columns" :data="data" />
      </div>
    </ResizablePanel>
    <ResizableHandle with-handle />
    <ResizablePanel :min-size="20">
      <PDFViewer ref="viewer" class="h-full" :documents="documents" :show-select="false" />
    </ResizablePanel>
  </ResizablePanelGroup>
</template>