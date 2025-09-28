<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue';
import { Minus } from 'lucide-vue-next';
import { toast } from 'vue-sonner';
import type { PageMachine } from '../machine-types';
import type { Row } from '@tanstack/vue-table';
import { axiosInstance } from '@/components/network-instance';

const props = defineProps<{
  getSelectedRows: () => Row<PageMachine>[],
  onMachinesDeleted: () => void
}>();

async function onDelete() {
  const selectedIds: number[] = props.getSelectedRows().map(row => row.getValue('machineId'));
  for (let selectedId of selectedIds) {
    await axiosInstance.post(`/machine/delete`, {
      machine_id: selectedId
    })
      .then(_response => {
        toast('Machine deleted', {
          description: `Machine ${selectedId} deleted`
        });
        props.onMachinesDeleted();
      })
      .catch(error => {
        if (error.response && error.response.status == 422)
          toast('Machine kept', {
            description: `Machine ${selectedId} kept, deleted associated documents before deleting machine`
          });
        else
          console.error(error);
      });
  }
}


</script>

<template>
  <Button @click="() => onDelete()" v-bind="$attrs">
    Delete
    <Minus class="ml-2 h-4 w-4" />
  </Button>
</template>