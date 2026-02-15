export interface Patient {
  id: string
  external_subject_id: string
  display_name: string
  subject_type: 'human' | 'veterinary'
  created_at: string
  updated_at: string
}

export interface Report {
  id: string
  patient_id: string
  original_filename: string
  file_hash_sha256: string
  status: string
  error_code?: string
  error_message?: string
  is_duplicate_of_report_id?: string
  created_at: string
  updated_at: string
}

export interface ParsedData {
  id: string
  report_id: string
  version_number: number
  version_type: string
  schema_version: string
  payload: any
  validation_status: string
  validation_errors?: any
  created_by: string
  created_at: string
}
