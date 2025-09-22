<script setup lang="ts" generic="TData, TValue">
import type { ColumnDef } from '@tanstack/vue-table'
import {
  FlexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useVueTable,
} from '@tanstack/vue-table'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import DocumentFilter from './DocumentFilter.vue';
import DocumentPage from './DocumentPage.vue';
import { ScrollArea } from '@/components/ui/scroll-area';
import { onBeforeUnmount, onMounted, useTemplateRef } from 'vue';

const props = defineProps<{
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}>();

const table = useVueTable({
  get data() { return props.data },
  get columns() { return props.columns },
  getCoreRowModel: getCoreRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getPaginationRowModel: getPaginationRowModel()
});

const container = useTemplateRef('container');
const filter = useTemplateRef('filter');
const page = useTemplateRef('page');
const header = useTemplateRef('header');
let resizeObserver: ResizeObserver;

function onResize() {
  if (!container.value || !filter.value || !page.value || !header.value) {
    console.warn('container for document table is null in resize');
    return;
  }
  table.setPageSize(Math.floor((container.value.offsetHeight - filter.value.$el.offsetHeight - page.value.$el.offsetHeight) / (header.value.$el.offsetHeight *0.97)));
}

onMounted(async () =>  {
  if (!container.value || !filter.value || !page.value || !header.value) {
    console.warn('container for document table is null after mount');
    return;
  }
  resizeObserver = new ResizeObserver(onResize);
  resizeObserver.observe(container.value);
  resizeObserver.observe(filter.value.$el);
  resizeObserver.observe(page.value.$el);
  resizeObserver.observe(header.value.$el);
})

onBeforeUnmount(async () => {
  if (!container.value || !filter.value || !page.value || !header.value)  {
    console.warn('container for document table is null before unmount');
    return;
  }
  resizeObserver.unobserve(container.value);
  resizeObserver.unobserve(filter.value.$el);
  resizeObserver.unobserve(page.value.$el);
  resizeObserver.unobserve(header.value.$el);
})

</script>

<template>
  <div class="relative h-full"  ref="container">
    <DocumentFilter :table="table" ref="filter" />
    <Table class="border rounded-md">
      <TableHeader ref="header">
        <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
          <TableHead v-for="header in headerGroup.headers" :key="header.id">
            <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
              :props="header.getContext()" />
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <template v-if="table.getRowModel().rows?.length">
          <TableRow v-for="row in table.getRowModel().rows" :key="row.id"
            :data-state="row.getIsSelected() ? 'selected' : undefined">
            <TableCell v-for="cell in row.getVisibleCells()" :key="cell.id">
              <FlexRender :render="cell.column.columnDef.cell" :props="cell.getContext()" />
            </TableCell>
          </TableRow>
        </template>
        <template v-else>
          <TableRow>
            <TableCell :colspan="columns.length" class="h-24 text-center overflow-hidden">
              No results.
            </TableCell>
          </TableRow>
        </template>
      </TableBody>
    </Table>
    <DocumentPage :table="table" class="absolute bottom-0 left-0 right-0" ref="page"/>
  </div>
</template>