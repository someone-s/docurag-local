<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue';
import { Minus } from 'lucide-vue-next';
import axios from 'axios';
import { toast } from 'vue-sonner';
import type { PageMachine } from '../machine-types';
import type { Row } from '@tanstack/vue-table';

const props = defineProps<{
  getSelectedRows: () =>  Row<PageMachine>[],
  onMachinesDeleted: () => void
}>();

async function onDelete() {
  const selectedIds: number[] = props.getSelectedRows().map(row => row.getValue('machineId'));
  for (let selectedId of selectedIds) {
    await axios.post(`http://0.0.0.0:8081/machine/delete`, {
      machine_id: selectedId
    });
    // no error
    toast('Machine deleted', {
      description: `Machine ${selectedId} deleted`
    });
    props.onMachinesDeleted();
  }
}


</script>

<template>
  <Button @click="() => onDelete()">Delete<Minus class="ml-2 h-4 w-4" /></Button>
</template>