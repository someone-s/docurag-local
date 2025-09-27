<script setup lang="ts">
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import Button from '@/components/ui/button/Button.vue';
import { Plus } from 'lucide-vue-next';
import { ref, type Ref } from 'vue';
import MachineAddMake from './MachineAddMake.vue';
import MachineAddCategory from './MachineAddCategory.vue';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import axios from 'axios';
import { toast } from 'vue-sonner';

const props = defineProps<{
  onMachineAdded: () => void
}>();

const make: Ref<string|null> = ref(null);
const name: Ref<string|null> = ref(null);
const category: Ref<string|null> = ref(null);
const model: Ref<string|null> = ref(null);


async function onSubmit() {

  if (!make.value) return;
  if (!name.value) return;
  if (!category.value) return;
  if (!model.value) return;

  await axios.post(`http://0.0.0.0:8081/machine/add`, {
    make: make.value,
    name: name.value,
    category: category.value,
    model: model.value,
  });

  // no error
  toast('Machine added', {
    description: `${make.value} ${model.value} added`,
  });

  props.onMachineAdded?.();
}

</script>

<template>
  <Popover>
    <PopoverTrigger as-child class="ml-auto cursor-pointer">
      <Button>
        Add Machine
        <Plus class="ml-2 h-4 w-4" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-fit max-w-screen flex flex-col">
      <div class="flex flex-col gap-3">
        <div class="flex flex-col gap-1">
          <Label>Make</Label>
          <MachineAddMake :set-select="(select) => make = select" />
        </div>
        <div class="flex flex-col gap-1">
          <Label>Category</Label>
          <MachineAddCategory :set-select="(select) => category = select" />
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