<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'
import LayoutHeader from '@/components/layout/LayoutHeader.vue';
import type { PDFDocument } from '@/components/pdf/pdf-types';
import PDFViewer from '@/components/pdf/PDFViewer.vue';
import DocumentTable from './DocumentTable.vue';
import { useTemplateRef } from 'vue';
import { axiosInstance } from '@/components/network-instance';

const documents: PDFDocument[] = [];

const fetchDocument = async (id: number) => {
  await navigator.locks.request('fetchDocument', async (_) => {
    if (!Number.isInteger(id)) return;

    if (documents.some(document => document.id == id)) return;


    const listResponse = await axiosInstance.get(`/document/fetch/${id}`,
      {
        responseType: 'arraybuffer',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/pdf'
        }
      });
    documents.push({
      name: `${id}`,
      id: id,
      file: listResponse.data
    });
  });
}

const viewer = useTemplateRef('viewer');

const openDocument = async (id: number) => {
  await fetchDocument(id);
  await viewer.value?.goToDocument(id);
}

</script>

<template>
  <LayoutHeader header-text="Document" />
  <ResizablePanelGroup direction="horizontal" class="h-full" auto-save-id="document-group">
    <ResizablePanel :min-size="40">
      <DocumentTable :open-document="openDocument" />
    </ResizablePanel>
    <ResizableHandle with-handle />
    <ResizablePanel :min-size="20">
      <PDFViewer ref="viewer" class="h-full" :documents="documents" :show-select="false" />
    </ResizablePanel>
  </ResizablePanelGroup>
</template>