<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'

import PDFViewer from '@/components/pdf/PDFViewer.vue';
import type { PDFDocument } from '@/components/pdf/pdf-types';
import ChatColumn from '@/components/chat/ChatColumn.vue';
import type { ChatEntry, ChatReference, ChatSegment } from '@/components/chat/chat-types';
import axios from 'axios';
import { parse, Allow } from "partial-json";
import { ref, useTemplateRef } from 'vue';

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


let activeSocket: WebSocket | null = null;
let partialResponse: string = "";
let entries: ChatEntry[] = [];
let updateKey = ref(0);
let processing: boolean = false;

function onMessage(event: MessageEvent<any>) {
  try {
    const data = JSON.parse(event.data);
    switch (data.type) {
      case 'document':
        fetchDocument(data.document_id, `${data.machine_make} ${data.machine_category} ${data.machine_model} ${data.document_category}`);
        break;
      case 'generate':
        partialResponse += data.delta;
        const partialObject = parse(partialResponse, Allow.STR | Allow.OBJ | Allow.ARR);
        if (partialObject.segments === undefined) break;

        const segments: any[] = partialObject.segments;
        entries[entries.length - 1].segments = segments
          .filter(inputSegment => inputSegment.text !== undefined)
          .map<ChatSegment>(inputSegment => {

            let reference: ChatReference | null = null;
            if (
              inputSegment.documentId !== undefined &&
              inputSegment.startPage !== undefined &&
              inputSegment.endPage !== undefined
            ) {
              reference = {
                documentId: inputSegment.documentId,
                startPage: inputSegment.startPage,
                endPage: inputSegment.endPage
              }
            }

            return {
              text: inputSegment.text,
              reference: reference
            }
          })
        updateKey.value++;
        break;
      case 'complete':
        partialResponse = "";

        chat.value?.scrollToBottom();
        break;
    }
  }
  catch (e) {
    console.error(e);
  }
}

function connect() {
  const newSocket = new WebSocket("ws://0.0.0.0:8081/query");
  newSocket.addEventListener('open', _ => {
    if (activeSocket != null) {
      try {
        activeSocket.close()
      }
      catch (_) { }
    }
    activeSocket = newSocket;
    partialResponse = "";
    entries = [];
  });
  newSocket.addEventListener('message', onMessage);
  newSocket.addEventListener('close', _ => activeSocket = null);
}

function setMachineMake(machineMake: string) {
  if (activeSocket == null) return;
  activeSocket.send(JSON.stringify({ type: 'data', parameter: 'machine_make', value: machineMake }));
}
function setMachineName(machineName: string) {
  if (activeSocket == null) return;
  activeSocket.send(JSON.stringify({ type: 'data', parameter: 'machine_name', value: machineName }));
}
function setMachineCategory(machineCategory: string) {
  if (activeSocket == null) return;
  activeSocket.send(JSON.stringify({ type: 'data', parameter: 'machine_category', value: machineCategory }));
}
function setMachineModel(machineModel: string) {
  if (activeSocket == null) return;
  activeSocket.send(JSON.stringify({ type: 'data', parameter: 'machine_model', value: machineModel }));
}

function sendQuery(query: string) {
  if (activeSocket == null) return;
  activeSocket.send(JSON.stringify({ type: 'command', action: 'generate', query: query }));
  entries.push({
    role: 'User',
    segments: [
      {
        text: query,
        reference: null
      }
    ]
  });
  entries.push({
    role: 'Assistant',
    segments: []
  });
  updateKey.value++;
}
function sendExit() {
  if (activeSocket == null) return;
  activeSocket.send(JSON.stringify({ type: 'command', action: 'exit' }));
}

connect();
</script>

<template>
  <ResizablePanelGroup direction="horizontal">
    <ResizablePanel>
      <ChatColumn ref="chat" class="h-full" :key="updateKey" :allow-edit="!processing" :entries="entries" :send-query="sendQuery"
        :goToSegment="goToSegment" />
    </ResizablePanel>
    <ResizableHandle with-handle />
    <ResizablePanel>
      <PDFViewer ref="viewer" class="h-full" :documents="documents" />
    </ResizablePanel>
  </ResizablePanelGroup>
</template>