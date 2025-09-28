<script setup lang="ts">
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import Button from '@/components/ui/button/Button.vue';
import { Plus } from 'lucide-vue-next';
import { ref, useTemplateRef, type Ref } from 'vue';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { toast } from 'vue-sonner';
import MachineMake from '../../filter/MachineMake.vue';
import MachineCategory from '../../filter/MachineCategory.vue';
import MachineMakeAddPopover from '../make/MachineMakeAddPopover.vue';
import MachineMakeDeletePopover from '../make/MachineMakeDeletePopover.vue';
import MachineCategoryAddPopover from '../category/MachineCategoryAddPopover.vue';
import MachineCategoryDeletePopover from '../category/MachineCategoryDeletePopover.vue';
import { axiosInstance } from '@/components/network-instance';

const props = defineProps<{
  onMachineAdded: () => void
}>();

const make: Ref<string | null> = ref(null);
const name: Ref<string | null> = ref(null);
const category: Ref<string | null> = ref(null);
const model: Ref<string | null> = ref(null);


async function onSubmit() {

  if (!make.value) return;
  if (!name.value) return;
  if (!category.value) return;
  if (!model.value) return;

  await axiosInstance.post(`/machine/add`, {
    make: make.value,
    name: name.value,
    category: category.value,
    model: model.value,
  });

  // no error
  toast('Machine added', {
    description: `${make.value} ${model.value} added`,
  });

  props.onMachineAdded();
}

const makeDropdown = useTemplateRef('make-dropdown');
const categoryDropdown = useTemplateRef('category-dropdown');

</script>

<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button class="cursor-pointer" v-bind="$attrs">
        Add
        <Plus class="ml-2 h-4 w-4" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-fit max-w-screen flex flex-col">
      <div class="flex flex-col gap-3">
        <div class="flex flex-col gap-1">
          <Label>Make</Label>
          <div class="flex flex-row gap-1">
            <MachineMake ref="make-dropdown" variant="ghost" :allow-unset="false"
              v-on:select="(select) => make = select" class="border rounded-md grow" />
            <div class="flex flex-row">
              <MachineMakeAddPopover variant="outline" class="size-9 border-r-0 rounded-r-none"
                v-on:make-added="(make) => {
                  makeDropdown?.setSelect(make);
                  makeDropdown?.fetchOptions();
                }" />
              <MachineMakeDeletePopover variant="outline" class="size-9 rounded-l-none" 
                :get-current-make="() => {
                  const currentSelect = makeDropdown?.getSelect();
                  return currentSelect ? currentSelect : null;
                }" 
                v-on:make-deleted="() => {
                  makeDropdown?.setSelect(null);
                  makeDropdown?.fetchOptions();
                }" />
            </div>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <Label>Category</Label>
          <div class="flex flex-row gap-1">
            <MachineCategory ref="category-dropdown" variant="ghost" :allow-unset="false"
              :onSelect="(select) => category = select" class="border rounded-md grow" />
            <div class="flex flex-row">
              <MachineCategoryAddPopover variant="outline" class="size-9 border-r-0 rounded-r-none"
                v-on:category-added="(category) => {
                  categoryDropdown?.setSelect(category);
                  categoryDropdown?.fetchOptions();
                }" />
              <MachineCategoryDeletePopover variant="outline" class="size-9 rounded-l-none" 
                :get-current-category="() => {
                  const currentSelect = categoryDropdown?.getSelect();
                  return currentSelect ? currentSelect : null;
                }" 
                v-on:category-deleted="() => {
                  categoryDropdown?.setSelect(null);
                  categoryDropdown?.fetchOptions();
                }" />
            </div>
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <Label>Model</Label>
          <Input class="max-w-3xs" placeholder="Model" @update:model-value="(value) => model = value.toString()" />
        </div>
        <div class="flex flex-col gap-1">
          <Label>Name</Label>
          <Input class="max-w-3xs" placeholder="Name" @update:model-value="(value) => name = value.toString()" />
        </div>
        <Button @click="onSubmit">
          Create
        </Button>

      </div>
    </PopoverContent>
  </Popover>
</template>