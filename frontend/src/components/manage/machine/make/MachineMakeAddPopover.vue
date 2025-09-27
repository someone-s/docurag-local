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

const make: Ref<string | null> = ref(null);


async function onSubmit() {

  if (!make) return;

  await axios.post(`http://0.0.0.0:8081/machine/make/add`, {
    machine_make: make.value
  }).then(_result => {
    toast('Make added', {
      description: `Make type ${make.value} added`,
    });
  }).catch(error => {
    if (error.response && error.response.status == 422)
      toast('Make already exists', {
        description: `Make type ${make.value} already exist`,
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
        Add Make
        <Plus class="ml-2 h-4 w-4" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-fit max-w-screen flex flex-col">
      <div class="flex flex-col gap-3">
        <div class="flex flex-col gap-1">
          <Label>Make</Label>
          <Input class="max-w-3xs" placeholder="Make" @update:model-value="(value) => make = value.toString()" />
        </div>
        <Button @click="onSubmit">
          Create
        </Button>
      </div>
    </PopoverContent>
  </Popover>
</template>