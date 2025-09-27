<script setup lang="ts" generic="TData, TValue">
import {
  FlexRender,
  getCoreRowModel,
  useVueTable,
} from '@tanstack/vue-table';
import {
  keepPreviousData,
  useInfiniteQuery,
} from '@tanstack/vue-query';
import {
  TableAbsolute,
  TableHeaderSticky
} from '@/components/ui/table-custom';
import {
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@/components/ui/table';
import { ref, useTemplateRef, watch, type Ref } from 'vue';
import { fetchData, type PageDocumentApiResponse } from './document-state';
import { getColumns, type PageDocument } from './document-types';
import { useVirtualizer } from '@tanstack/vue-virtual';
import MachineFilter from './MachineFilter.vue';
import DocumentProgress from './progress/DocumentProgress.vue';
import axios from 'axios';
import { toast } from 'vue-sonner';
import DocumentAddPopover from './add/DocumentAddPopover.vue';
import { Button } from '@/components/ui/button';
import { Minus } from 'lucide-vue-next';

const props = defineProps<{
  openDocument: (id: number) => void
}>();

const openDocumentLocal = (id: number) => {
  props.openDocument(id);
}

const fetchSize = 50;
const manualRefresh = ref(0);
const machineIds: Ref<number[] | null> = ref(null);

const {
  data,
  fetchNextPage,
  hasNextPage,
  isFetching
} = useInfiniteQuery<PageDocumentApiResponse>({
  queryKey: ['pageDocument', machineIds, manualRefresh],
  queryFn: async ({ pageParam = 0 }) => {
    const start = (pageParam as number) * fetchSize;
    const fetchedData = await fetchData(start, fetchSize, machineIds.value);
    return fetchedData;
  },
  initialPageParam: 0,
  getNextPageParam: (lastGroup, groups) => lastGroup.data.length == fetchSize ? groups.length : null,
  refetchOnWindowFocus: false,
  placeholderData: keepPreviousData,
});

const flatdata: Ref<PageDocument[]> = ref(data.value?.pages.flatMap(page => page.data) ?? []);
watch(data, (current, _) => {
  flatdata.value = current?.pages.flatMap(page => page.data) ?? [];
});

const tableElement = useTemplateRef('tableElement');

watch([tableElement, isFetching, hasNextPage], async ([currentTableElement, currentIsFetching, currentHasNextPage], _) => {
  if (currentTableElement?.$el == null) return;

  const { scrollHeight, scrollTop, clientHeight } = currentTableElement.$el as HTMLElement;

  if (scrollHeight - scrollTop - clientHeight < 500 && !currentIsFetching && currentHasNextPage)
    fetchNextPage();
});

const columns = getColumns(openDocumentLocal);

const table = useVueTable({
  get data() { return flatdata.value },
  get columns() { return columns },
  getCoreRowModel: getCoreRowModel(),
  debugTable: true,
});

const { rows } = table.getRowModel();

const rowVirtualizer = useVirtualizer({
  count: rows.length,
  estimateSize: () => 33, //estimate row height for accurate scrollbar dragging
  getScrollElement: () => tableElement.value?.$el,
  //measure dynamic row height, except in firefox because it measures table border height incorrectly
  measureElement:
    typeof window !== 'undefined' &&
      navigator.userAgent.indexOf('Firefox') === -1
      ? element => element?.getBoundingClientRect().height
      : undefined,
  overscan: 5,
});

watch(machineIds, (_current, _past) => {
  rowVirtualizer.value.scrollToIndex?.(0)
});

async function onDelete() {
  const selectedIds: number[] = table.getSelectedRowModel().flatRows.map(row => row.getValue('documentId'));
  for (let selectedId of selectedIds) {
    await axios.post(`http://0.0.0.0:8081/document/delete`, {
      document_id: selectedId
    });
    // no error
    toast('Document deleted', {
      description: `Document ${selectedId} deleted`
    });
    manualRefresh.value++;
    table.resetRowSelection();
  }
}

</script>

<template>
  <div class="size-full relative">
    <div class="absolute top-0 left-0 right-0 bottom-0 p-3 flex flex-col">
      <div class="flex items-center py-4 gap-2 flex-wrap">
        <MachineFilter :table="table"
          :set-machines="(machines) => { machineIds = machines ? machines.map(machine => machine.machineId) : null }" />
        <DocumentAddPopover />
        <Button @click="() => onDelete()">Delete<Minus class="ml-2 h-4 w-4" /></Button>
      </div>
      <DocumentProgress class="mb-2" v-on:progress-complete="() => manualRefresh++" />
      <TableAbsolute container-class="border rounded-md">
        <TableHeaderSticky>
          <TableRow v-for="headerGroup in table.getHeaderGroups()" :key="headerGroup.id">
            <TableHead v-for="header in headerGroup.headers" :key="header.id">
              <FlexRender v-if="!header.isPlaceholder" :render="header.column.columnDef.header"
                :props="header.getContext()" />
            </TableHead>
          </TableRow>
        </TableHeaderSticky>
        <TableBody ref="tableElement">
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
      </TableAbsolute>
    </div>
  </div>
</template>