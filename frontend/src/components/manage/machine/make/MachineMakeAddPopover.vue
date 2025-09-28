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
import { toast } from 'vue-sonner';
import { axiosInstance } from '@/components/network-instance';

const props = defineProps<{
  onMakeAdded: (make: string) => void
}>();

const make: Ref<string | null> = ref(null);


async function onSubmit() {

  const currentMake = make.value;

  if (!currentMake) return;

  await axiosInstance.post(`/machine/make/add`, {
    machine_make: currentMake
  }).then(_result => {
    toast('Make added', {
      description: `Make type ${currentMake} added`,
    });
    props.onMakeAdded(currentMake);
  }).catch(error => {
    if (error.response && error.response.status == 422)
      toast('Make already exists', {
        description: `Make type ${currentMake} already exist`,
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
          <Input class="max-w-3xs" placeholder="Make" @update:model-value="(value) => make = value.toString()" />
        </div>
        <Button @click="onSubmit">
          Create
        </Button>
      </div>
    </PopoverContent>
  </Popover>
</template>