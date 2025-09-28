import { axiosInstance } from "@/components/network-instance"
import type { PageMachine } from "./machine-types"

export type PageMachineApiResponse = {
  data: PageMachine[]
}

export const fetchData = async (
  start: number,
  size: number,
  make: string | null,
  category: string | null,
  modelPartial: string | null
): Promise<PageMachineApiResponse> => {

  const params: { [key: string]: any } = {}
  params.start_position = start;
  params.limit = size;
  if (make)
    params.machine_make = make;
  if (category)
    params.machine_category = category;
  if (modelPartial)
    params.machine_model = modelPartial;

  const response = await axiosInstance.get('/machine/search', {
    params: params
  });

  const machines: any[] = response.data.machines;

  return {
    data: machines.map(obj => {
      return {
        machineId: obj.id,
        machineMake: obj.make,
        machineName: obj.name,
        machineCategory: obj.category,
        machineModel: obj.model
      }
    })
  }
}