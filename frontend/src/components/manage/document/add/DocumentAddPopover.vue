<script setup lang="ts">
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import Button from '@/components/ui/button/Button.vue';
import { Minus, Plus } from 'lucide-vue-next';
import { ref, useTemplateRef } from 'vue';
import DocumentAddMachine from './DocumentAddMachine.vue';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import axios from 'axios';
import DocumentAddDocumentCategory from './DocumentAddDocumentCategory.vue';

const machineCount = ref(1);
const itemEls = useTemplateRef('items');

const fileEl = useTemplateRef('file');

const categoryEl = useTemplateRef('category');

function onSubmit() {
  const files = fileEl.value?.$el.files;
  if (!files || files.length < 1)
    return;

  const machines = itemEls.value?.map(item => item?.getId());
  if (!machines || machines.some(machine => machine == null))
    return;

  const category = categoryEl.value?.getCategory();
  if (!category)
    return;

  axios.postForm(`http://0.0.0.0:8081/document/upload`, {
    machine_ids_str: machines.join(','),
    document_category: category,
    file: files[0]
  })
}

</script>

<template>
  <Popover>
    <PopoverTrigger as-child class="ml-auto cursor-pointer">
      <Button>
        Add
        <Plus class="ml-2 h-4 w-4" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-fit max-w-screen flex flex-col">
      <div class="flex flex-col gap-3">
        <div class="flex flex-col gap-1">
          <div class="flex flex-row justify-between">
            <Label>Machines</Label>
            <div>
              <Button variant="outline" class="size-7 rounded-r-none" @click="machineCount += 1">
                <Plus class="size-4" />
              </Button>
              <Button variant="outline" class="size-7 rounded-l-none"
                @click="machineCount = Math.max(1, machineCount - 1)">
                <Minus class="size-4" />
              </Button>
            </div>
          </div>
          <div class="flex flex-col gap-1">
            <DocumentAddMachine v-for="_ in machineCount" ref="items" />
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <Label class="h-7">Document</Label>
          <div class="flex flex-row gap-1">
            <Input type="file" accept="application/pdf" ref="file" />
            <DocumentAddDocumentCategory ref="category" />
          </div>
        </div>
        <Button @click="onSubmit">
          Submit and Process
        </Button>

      </div>
    </PopoverContent>
  </Popover>
</template>