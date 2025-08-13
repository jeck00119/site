// Process Module Types

export interface ProcessState {
  inspectionResults: any[];
  currentInspectionResult: any | null;
  excelBlob: any | null;
  excelBlobPath: any | null;
  capabilityState: any | null;
  offsetState: any | null;
  itacState: any | null;
  processStatus: string;
  dmc: any | null;
}
