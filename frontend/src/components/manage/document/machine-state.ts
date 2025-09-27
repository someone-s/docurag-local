import axios from "axios";
import type { PageMachine } from "./machine-types";

export type PageMachineApiResponse = {
  machines: PageMachine[]
}

export const fetchAllMachine = async (
  make: string|null,
  category: string|null,
  model: string|null
): Promise<PageMachineApiResponse> => {

  const params: { [key: string]: any } = {};

  if (make)
    params.machine_make = make;
  if (category)
    params.machine_category = category;
  if (model)
    params.machine_model = model;

  const response = await axios.get('http://0.0.0.0:8081/machine/search', {
    params: params
  });
  const machines: any[] = response.data.machines;

  return {
    machines: machines.map(obj => {
      return {
        machineId: obj.id,
        machineMake: obj.make,
        machineName: obj.name,
        machineCategory: obj.category,
        machineModel: obj.model,
      }
    })
  }
}
