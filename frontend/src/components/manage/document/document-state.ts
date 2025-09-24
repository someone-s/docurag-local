import type { PageDocument } from "./document-types"
import axios from "axios"

export type PageDocumentApiResponse = {
  data: PageDocument[]
}

export const fetchData = async (
  start: number,
  size: number,
  machine_ids: number[]|null
): Promise<PageDocumentApiResponse> => {

  if (machine_ids != null && machine_ids.length == 0)
    return {
      data: []
    }

  const params: { [key: string]: any } = {}
  params.start_position = start;
  params.limit = size;
  if (machine_ids != null)
    params.machine_ids_string = machine_ids.join(',');

  const response = await axios.get('http://0.0.0.0:8081/document/search', {
    params: params
  });

  const documents: any[] = response.data.documents;

  return {
    data: documents.map(obj => {
      return {
        documentId: obj.document_id,
        documentCategory: obj.document_category,
        machines: (obj.machines as any[]).map(machine => {
          return {
            machineId: machine.id,
            machineMake: machine.make,
            machineName: machine.name,
            machineCategory: machine.category,
            machineModel: machine.model
          }})
        }
      }
    )
  }
}