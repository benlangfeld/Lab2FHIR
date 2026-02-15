import axios from 'axios'
import type { Patient, Report, ParsedData } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Patients
export const getPatients = async (): Promise<{ patients: Patient[]; total: number }> => {
  const { data } = await api.get('/patients')
  return data
}

export const createPatient = async (patient: {
  external_subject_id: string
  display_name: string
  subject_type: 'human' | 'veterinary'
}): Promise<Patient> => {
  const { data } = await api.post('/patients', patient)
  return data
}

// Reports
export const getReports = async (patientId?: string): Promise<{ reports: Report[]; total: number }> => {
  const { data } = await api.get('/reports', {
    params: patientId ? { patient_id: patientId } : undefined,
  })
  return data
}

export const uploadReport = async (patientId: string, file: File): Promise<Report> => {
  const formData = new FormData()
  formData.append('patient_id', patientId)
  formData.append('file', file)

  const { data } = await api.post('/reports', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

export const getReport = async (reportId: string): Promise<Report> => {
  const { data } = await api.get(`/reports/${reportId}`)
  return data
}

// Parsed Data
export const getParsedData = async (reportId: string): Promise<ParsedData> => {
  const { data } = await api.get(`/parsed-data/${reportId}`)
  return data
}

// Bundles
export const generateBundle = async (reportId: string): Promise<Record<string, unknown>> => {
  const { data } = await api.post(`/bundles/${reportId}/generate`)
  return data
}

export const downloadBundle = async (reportId: string): Promise<Record<string, unknown>> => {
  const { data } = await api.get(`/bundles/${reportId}/download`)
  return data
}
