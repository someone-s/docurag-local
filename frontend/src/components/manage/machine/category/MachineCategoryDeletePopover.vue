<script setup lang="ts">
import Button from '@/components/ui/button/Button.vue';
import { Minus } from 'lucide-vue-next';
import { toast } from 'vue-sonner';
import { axiosInstance } from '@/components/network-instance';

const props = defineProps<{
  getCurrentCategory: () => string|null,
  onCategoryDeleted: () => void
}>();

async function onSubmit() {

  const category = props.getCurrentCategory();

  if (!category) return;

  await axiosInstance.post(`/machine/category/delete`, {
    machine_category: category
  }).then(_result => {
    toast('Category deleted', {
      description: `Category type ${category} deleted`,
    });
    props.onCategoryDeleted();
  }).catch(error => {
    if (error.response && error.response.status == 422)
      toast('Category kept', {
        description: `Category type ${category} kept as it is inuse`,
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