<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue';
import { Minus } from 'lucide-vue-next';
import { toast } from 'vue-sonner';
import type { PageDocument } from '../document-types';
import type { Row } from '@tanstack/vue-table';
import { axiosInstance } from '@/components/network-instance';

const props = defineProps<{
  getSelectedRows: () =>  Row<PageDocument>[],
  onDocumentsDeleted: () => void
}>();

async function onDelete() {
  const selectedIds: number[] = props.getSelectedRows().map(row => row.getValue('documentId'));
  for (let selectedId of selectedIds) {
    await axiosInstance.post(`/document/delete`, {
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