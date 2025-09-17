

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
import type { PDFDocument } from './PDFDocument';

const props = defineProps<{
  documents: PDFDocument[]
}>();

const emit = defineEmits<{
  (e: 'change', id: number): void
}>()
</script>
 
<template>
  <div class="absolute isolate left-0 right-0 top-3 flex  justify-center">

    <Select v-on:update:model-value="(id: AcceptableValue) => emit('change', id as number)">
      <SelectTrigger  class="w-80 bg-background">
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