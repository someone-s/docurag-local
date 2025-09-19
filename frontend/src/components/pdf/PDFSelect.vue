

<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { AcceptableValue } from 'reka-ui';
import type { PDFDocument } from './pdf-types';
import { useLoaderCapability, type LoaderCapability } from '@embedpdf/plugin-loader/vue';

const { provides: loaderProvides } = useLoaderCapability();

let currentId: number = -1;

async function onchange(loaderProvides: LoaderCapability, id: number) {

  if (id == currentId) return;
  currentId = id;
  const document = props.documents.find(document => document.id == id);
  if (document == null) return;

  await loaderProvides.loadDocument({
    type: 'buffer',
    pdfFile: { 
      id: crypto.randomUUID(), 
      name: document.name,
      content: document.file 
    },
    // Can specify password in optional open options
  });

  props.reload()

}

const props = defineProps<{
  documents: PDFDocument[]
  reload: () => void
}>();

async function changeDocument(id: number) {
  if (loaderProvides.value == null) return;
  await onchange(loaderProvides.value, id);
}

defineExpose({
  changeDocument
})
</script>
 
<template>
  <div class="absolute isolate left-0 right-0 top-3 flex  justify-center no-drag">

    <Select :model-value="documents.find(document => document.id == currentId)?.name ?? 'Choose Document'" v-on:update:model-value="(id: AcceptableValue) => { if (loaderProvides != null) onchange(loaderProvides, id as number) }">
      <SelectTrigger  class="w-80 bg-background dark:bg-background hover:bg-accent dark:hover:bg-accent">
        <SelectValue placeholder="Choose Document" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
        <SelectItem v-for="document in props.documents" :value="document.id">{{document.name}}</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
    
  </div>
</template>