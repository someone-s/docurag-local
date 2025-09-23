import type { PageDocument } from "./document-types"
import axios from "axios"

export type PageDocumentApiResponse = {
  data: PageDocument[]
}

export const fetchData = async (
  start: number,
  size: number,
  machine_ids: number[]
): Promise<PageDocumentApiResponse> => {

  const response = await axios.get('http://0.0.0.0:8081/document/search', {
    params: {
      start_position: start,
      limit: size,
      machine_ids_string: machine_ids.join(',')
    }
  });

  const documents: any[] = response.data.documents;

  return {
    data: documents.map(obj => {
      return {
        documentId: obj.document_id,
        documentCategory: obj.document_category,
        machineId: obj.machine_id,
        machineMake: obj.machine_make,
        machineName: obj.machine_name,
        machineCategory: obj.machine_category,
        machineModel: obj.machine_model
      }
    })
  }
}