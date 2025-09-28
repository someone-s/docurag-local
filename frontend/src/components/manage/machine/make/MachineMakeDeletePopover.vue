<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue';
import { Minus } from 'lucide-vue-next';
import { toast } from 'vue-sonner';
import { axiosInstance } from '@/components/network-instance';

const props = defineProps<{
  getCurrentMake: () => string|null,
  onMakeDeleted: () => void
}>();

async function onSubmit() {

  const make = props.getCurrentMake();

  if (!make) return;

  await axiosInstance.post(`/machine/make/delete`, {
    machine_make: make
  }).then(_result => {
    toast('Make deleted', {
      description: `Make type ${make} deleted`,
    });
    props.onMakeDeleted();
  }).catch(error => {
    if (error.response && error.response.status == 422)
      toast('Make kept', {
        description: `Make type ${make} kept as it is inuse`,
      });
    else
      console.error(error);
  })
}

</script>

<template>
  <Button class="cursor-pointer" v-bind="$attrs" @click="() => onSubmit()">
    <Minus class="h-4 w-4" />
  </Button>
</template>