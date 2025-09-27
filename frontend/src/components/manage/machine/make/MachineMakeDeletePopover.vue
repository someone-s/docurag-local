<script setup lang="ts">
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import Button from '@/components/ui/button/Button.vue';
import { Minus } from 'lucide-vue-next';
import { ref, type Ref } from 'vue';
import { Label } from '@/components/ui/label';
import axios from 'axios';
import { toast } from 'vue-sonner';
import MachineMake from '../../filter/MachineMake.vue';

const make: Ref<string|null> = ref(null);

async function onSubmit() {

  if (!make) return;

  await axios.post(`http://0.0.0.0:8081/machine/make/delete`, {
    machine_make: make.value
  }).then(_result => {
    toast('Make deleted', {
      description: `Make type ${make.value} deleted`,
    });
  }).catch(error => {
    if (error.response && error.response.status == 422)
      toast('Make kept', {
        description: `Make type ${make.value} kept as it is inuse`,
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
        Delete Make
        <Minus class="ml-2 h-4 w-4" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-fit max-w-screen flex flex-col">
      <div class="flex flex-col gap-3">
        <div class="flex flex-col gap-1">
          <Label>Make</Label>
          <MachineMake variant="ghost" :allow-unset="false" :set-select="(select) => make = select" class="border rounded-md" />
        </div>
        <Button @click="onSubmit">
          Delete
        </Button>
      </div>
    </PopoverContent>
  </Popover>
</template>