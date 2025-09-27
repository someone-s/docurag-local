<script setup lang="ts">
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import Button from '@/components/ui/button/Button.vue';
import { Plus } from 'lucide-vue-next';
import { ref, type Ref } from 'vue';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import axios from 'axios';
import { toast } from 'vue-sonner';

const props = defineProps<{
  onCategoryAdded: (make: string) => void
}>();

const category: Ref<string | null> = ref(null);


async function onSubmit() {

  const currentCategory = category.value;

  if (!currentCategory) return;

  await axios.post(`http://0.0.0.0:8081/document/category/add`, {
    document_category: currentCategory
  }).then(_result => {
    toast('Category added', {
      description: `Category type ${currentCategory} added`,
    });
    props.onCategoryAdded(currentCategory);
  }).catch(error => {
    if (error.response && error.response.status == 422)
      toast('Category already exists', {
        description: `Category type ${currentCategory} already exist`,
      });
    else
      console.error(error);
  })
}

</script>

<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button class="cursor-pointer" v-bind="$attrs">
        <Plus class="h-4 w-4" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-fit max-w-screen flex flex-col">
      <div class="flex flex-col gap-3">
        <div class="flex flex-col gap-1">
          <Label>Make</Label>
          <Input class="max-w-3xs" placeholder="Category" @update:model-value="(value) => category = value.toString()" />
        </div>
        <Button @click="onSubmit">
          Create
        </Button>
      </div>
    </PopoverContent>
  </Popover>
</template>