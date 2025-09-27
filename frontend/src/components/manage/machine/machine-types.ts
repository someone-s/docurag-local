import Checkbox from '@/components/ui/checkbox/Checkbox.vue';
import type { ColumnDef } from '@tanstack/vue-table';
import { h } from 'vue';


export interface PageMachine {
  machineId: number,
  machineMake: string,
  machineName: string,
  machineCategory: string,
  machineModel: string
}


export const columns: ColumnDef<PageMachine>[] = [
  {
    id: "select",
    header: ({ table }) => h(Checkbox, {
      class: 'text-left ',
      modelValue: table.getIsAllPageRowsSelected() || (table.getIsSomePageRowsSelected() && "indeterminate"),
      "onUpdate:modelValue": value => table.toggleAllPageRowsSelected(!!value),
      ariaLabel: "Select all",
    }),
    cell: ({ row }) => h(Checkbox, {
      modelValue: row.getIsSelected(),
      "onUpdate:modelValue": value => row.toggleSelected(!!value),
      ariaLabel: "Select row",
    }),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'machineId',
    header: () => h('div', { class: 'text-left' }, 'ID'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium' }, row.getValue('machineId')),
  },
  {
    accessorKey: 'machineMake',
    header: () => h('div', { class: 'text-left ' }, 'Make'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium break-normal' }, row.getValue('machineMake')),
  },
  {
    accessorKey: 'machineName',
    header: () => h('div', { class: 'text-left ' }, 'Name'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium break-normal' }, row.getValue('machineName')),
  },
  {
    accessorKey: 'machineCategory',
    header: () => h('div', { class: 'text-left' }, 'Category'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium' }, row.getValue('machineCategory')),
  },
  {
    accessorKey: 'machineModel',
    header: () => h('div', { class: 'text-left' }, 'Model'),
    cell: ({ row }) => h('div', { class: 'text-left font-medium' }, row.getValue('machineModel')),
  },
];