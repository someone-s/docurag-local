import Checkbox from '@/components/ui/checkbox/Checkbox.vue';
import type { ColumnDef } from '@tanstack/vue-table';
import { h } from 'vue';




export interface PageDocument {
  documentId: number
  documentCategory: string
  machineId: number,
  machineMake: string,
  machineName: string,
  machineCategory: string,
  machineModel: string
}


export const columns: ColumnDef<PageDocument>[] = [
   {
    id: "select",
    header: ({ table }) => h(Checkbox, {
      class: 'text-left ',
      modelValue: table.getIsAllPageRowsSelected() || (table.getIsSomePageRowsSelected() && "indeterminate"),
      "onUpdate:modelValue": value => table.toggleAllPageRowsSelected(!!value),
      ariaLabel: "Select all",
    }),
    cell: ({ row }) => h(Checkbox, {
      "modelValue": row.getIsSelected(),
      "onUpdate:modelValue": value => row.toggleSelected(!!value),
      "ariaLabel": "Select row",
    }),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'documentId',
    header: () => h('div', { class: 'text-left' }, 'ID'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium' }, row.getValue('documentId')),
  },
  {
    accessorKey: 'machineMake',
    header: () => h('div', { class: 'text-left ' }, 'Make'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium' }, row.getValue('machineMake')),
  },
  {
    accessorKey: 'machineCategory',
    header: () => h('div', { class: 'text-left' }, 'Machine'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium' }, row.getValue('machineCategory')),
  },
  {
    accessorKey: 'machineModel',
    header: () => h('div', { class: 'text-left' }, 'Machine'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium' }, row.getValue('machineModel')),
  },
  {
    accessorKey: 'documentCategory',
    header: () => h('div', { class: 'text-left' }, 'Category'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium' }, row.getValue('documentCategory')),
  },
]