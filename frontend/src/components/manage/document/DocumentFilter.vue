<script setup lang="ts">
import Input from '@/components/ui/input/Input.vue';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuCheckboxItem
} from '@/components/ui/dropdown-menu';
import Button from '@/components/ui/button/Button.vue';
import { ChevronDown } from 'lucide-vue-next';
import type { Table } from '@tanstack/vue-table';


defineProps<{
  table: Table<any>
}>();
</script>

<template>
  <div class="flex items-center py-4">
    <Input class="max-w-sm" placeholder="Filter emails..."
      :model-value="(table.getColumn('email')?.getFilterValue() as string)" 
      @update:model-value="table.getColumn('email')?.setFilterValue($event)" />
    <DropdownMenu>
      <DropdownMenuTrigger as-child>
        <Button variant="outline" class="ml-auto">
          Columns
          <ChevronDown class="ml-2 h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuCheckboxItem v-for="column in table.getAllColumns().filter((column) => column.getCanHide())"
          :key="column.id" class="capitalize" :model-value="column.getIsVisible()" @update:model-value="(value) => {
            column.toggleVisibility(!!value)
          }">
          {{ column.id }}
        </DropdownMenuCheckboxItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
</template>