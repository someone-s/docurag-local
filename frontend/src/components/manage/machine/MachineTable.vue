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
import { fetchData, type PageMachineApiResponse } from './machine-state';
import { columns, type PageMachine } from './machine-types';
import { useVirtualizer } from '@tanstack/vue-virtual';
import MachineMake from '../filter/MachineMake.vue';
import MachineCategory from '../filter/MachineCategory.vue';
import Input from '@/components/ui/input/Input.vue';
import MachineAddPopover from './add/MachineAddPopover.vue';
import MachineDelete from './delete/MachineDelete.vue';


const fetchSize = 50;
const manualRefresh = ref(0);

const make: Ref<string|null> = ref(null);
const category: Ref<string|null> = ref(null);
const model: Ref<string> = ref('');

const {
  data,
  fetchNextPage,
  hasNextPage,
  isFetching
} = useInfiniteQuery<PageMachineApiResponse>({
  queryKey: ['pageMachine', make, category, model, manualRefresh],
  queryFn: async ({ pageParam = 0 }) => {
    const start = (pageParam as number) * fetchSize;
    const fetchedData = await fetchData(start, fetchSize, make.value, category.value, model.value);
    return fetchedData;
  },
  initialPageParam: 0,
  getNextPageParam: (lastGroup, groups) => lastGroup.data.length == fetchSize ? groups.length : null,
  refetchOnWindowFocus: false,
  placeholderData: keepPreviousData,
});

const flatdata: Ref<PageMachine[]> = ref(data.value?.pages.flatMap(page => page.data) ?? []);
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

watch([make, category, model], (_current, _past) => {
  rowVirtualizer.value.scrollToIndex?.(0)
});

function clearSelection() {
  manualRefresh.value++;
  table.resetRowSelection();
}

</script>

<template>
  <div class="size-full relative">
    <div class="absolute top-0 left-0 right-0 bottom-0 p-3 flex flex-col">
      <div class="flex items-center py-4 gap-2 flex-wrap">
        <MachineMake :set-select="(select) => make = select" />
        <MachineCategory :set-select="(select) => category = select" />
        <Input class="max-w-3xs" placeholder="Model" @update:model-value="(value) => model = value.toString()" />
        <MachineAddPopover v-on:machine-added="() => manualRefresh++" />
        <MachineDelete :get-selected-rows="() => table.getSelectedRowModel().flatRows" v-on:machines-deleted="clearSelection" />
      </div>
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