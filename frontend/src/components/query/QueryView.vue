<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'

import PDFViewer from '@/components/pdf/PDFViewer.vue';
import type { PDFDocument } from '@/components/pdf/pdf-types';
import ChatColumn from '@/components/chat/ChatColumn.vue';
import axios from 'axios';
import { onUnmounted, useTemplateRef } from 'vue';
import { QueryState } from './query-state';
import { QueryFilter } from './query-filter';
import type { ChatOptions } from '../chat/chat-types';
import LayoutHeader from '../layout/LayoutHeader.vue';

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

const viewer = useTemplateRef('viewer');

function goToSegment(documentId: number, startPage: number, _endPage: number) {
  if (viewer.value == null) return;
  viewer.value.goToDocumentPage(documentId, startPage);
}

const chat = useTemplateRef('chat');



const queryState = new QueryState(
  (documentId, documentCategory, machineMake, machineCategory, machineModel) => fetchDocument(documentId, `${machineMake} ${machineCategory} ${machineModel} ${documentCategory}`),
  () => chat.value?.scrollToBottom()
);

function onChange(options: ChatOptions) {
  queryState.setEmpty();
  if (options.makeCurrent)
    queryState.setMachineMake(options.makeCurrent);
  if (options.categoryCurrent)
    queryState.setMachineCategory(options.categoryCurrent);
  if (options.modelCurrent)
    queryState.setMachineModel(options.modelCurrent);
}

const queryFilter = new QueryFilter(
  (_, options) => onChange(options), (_, options) => onChange(options), (_, options) => onChange(options)
);

onUnmounted(() => {
  queryState.sendExit();
});


</script>

<template>
  <LayoutHeader header-text="Query" />
  <ResizablePanelGroup direction="horizontal" class="h-full" auto-save-id="query-group">
    <ResizablePanel :min-size="40">
      <ChatColumn ref="chat" class="h-full" 
        :block="queryState.processing"
        :entries="queryState.entries" 
        :send-query="query => queryState.sendQuery(query)" 
        :goToSegment="goToSegment"
        :options="queryFilter.options"
        :set-make="(val) => queryFilter.setMake(val)"
        :set-category="(val) => queryFilter.setCategory(val)"
        :set-model="(val) => queryFilter.setModel(val)" />
    </ResizablePanel>
    <ResizableHandle with-handle />
    <ResizablePanel :min-size="20">
      <PDFViewer ref="viewer" class="h-full" :documents="documents" :show-select="true" />
    </ResizablePanel>
  </ResizablePanelGroup>
</template>