<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue';
import { Minus } from 'lucide-vue-next';
import axios from 'axios';
import { toast } from 'vue-sonner';
import type { PageDocument } from '../document-types';
import type { Row } from '@tanstack/vue-table';

const props = defineProps<{
  getSelectedRows: () =>  Row<PageDocument>[],
  onDocumentsDeleted: () => void
}>();

async function onDelete() {
  const selectedIds: number[] = props.getSelectedRows().map(row => row.getValue('documentId'));
  for (let selectedId of selectedIds) {
    await axios.post(`http://0.0.0.0:8081/document/delete`, {
      document_id: selectedId
    });
    // no error
    toast('Document deleted', {
      description: `Document ${selectedId} deleted`
    });
    props.onDocumentsDeleted();
  }
}


</script>

<template>
  <Button @click="() => onDelete()">Delete<Minus class="ml-2 h-4 w-4" /></Button>
</template>