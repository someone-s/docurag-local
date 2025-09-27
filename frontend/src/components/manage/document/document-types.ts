import { Button } from '@/components/ui/button';
import { FileSymlinkIcon } from 'lucide-vue-next';
import Checkbox from '@/components/ui/checkbox/Checkbox.vue';
import type { ColumnDef } from '@tanstack/vue-table';
import { h } from 'vue';
import type { PageMachine } from './machine-types';


export interface PageDocument {
  documentId: number
  documentCategory: string
  machines: PageMachine[]
}


export const getColumns = (openDocument: (id: number) => void): ColumnDef<PageDocument>[] => {
  return [
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
      accessorKey: 'machines',
      header: () => h('div', { class: 'text-left ' }, 'Make'),
      cell: ({ row }) => h('div', { class: 'text-left font-medium break-normal' }, [... new Set((row.getValue('machines') as PageMachine[]).map(machine => `${machine.machineMake}`))].join()),
    },
    {
      accessorKey: 'machines',
      header: () => h('div', { class: 'text-left ' }, 'Model'),
      cell: ({ row }) => h('div', { class: 'text-left font-medium break-normal' }, (row.getValue('machines') as PageMachine[]).map(machine => `${machine.machineModel}`).join()),
    },
    {
      accessorKey: 'documentCategory',
      header: () => h('div', { class: 'text-left' }, 'Category'),
      cell: ({ row }) => h('div', { class: 'text-left font-medium' }, row.getValue('documentCategory')),
    },
    {
      accessorKey: 'view',
      header: () => h('div', { class: 'text-left' }, 'View'),
      cell: ({ row }) => h(Button, { variant: 'ghost', class: 'cursor-pointer', onClick: () => openDocument(Number.parseInt(row.getValue('documentId'))) }, () => h(FileSymlinkIcon, { class: 'size-4' })),
    },
  ]
}