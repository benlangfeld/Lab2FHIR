import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getPatients, createPatient } from '../services/api'
import type { Patient } from '../types'
import './PatientsPage.css'

export default function PatientsPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    external_subject_id: '',
    display_name: '',
    subject_type: 'human' as 'human' | 'veterinary',
  })

  const { data, isLoading, error } = useQuery({
    queryKey: ['patients'],
    queryFn: getPatients,
  })

  const createMutation = useMutation({
    mutationFn: createPatient,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] })
      setShowForm(false)
      setFormData({
        external_subject_id: '',
        display_name: '',
        subject_type: 'human',
      })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  if (isLoading) return <div className="loading">Loading patients...</div>
  if (error) return <div className="error">Error loading patients: {(error as Error).message}</div>

  return (
    <div className="patients-page">
      <div className="page-header">
        <h1>Patients</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Patient'}
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <h2>Create New Patient</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="external_subject_id">Patient ID</label>
              <input
                type="text"
                id="external_subject_id"
                value={formData.external_subject_id}
                onChange={(e) => setFormData({ ...formData, external_subject_id: e.target.value })}
                required
                placeholder="e.g., patient-001"
              />
            </div>

            <div className="form-group">
              <label htmlFor="display_name">Display Name</label>
              <input
                type="text"
                id="display_name"
                value={formData.display_name}
                onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                required
                placeholder="e.g., John Doe"
              />
            </div>

            <div className="form-group">
              <label htmlFor="subject_type">Subject Type</label>
              <select
                id="subject_type"
                value={formData.subject_type}
                onChange={(e) => setFormData({ ...formData, subject_type: e.target.value as 'human' | 'veterinary' })}
              >
                <option value="human">Human</option>
                <option value="veterinary">Veterinary</option>
              </select>
            </div>

            <button type="submit" className="btn btn-primary" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Patient'}
            </button>

            {createMutation.isError && (
              <div className="error-message">
                Error: {(createMutation.error as Error).message}
              </div>
            )}
          </form>
        </div>
      )}

      <div className="patients-list">
        {data?.patients.length === 0 ? (
          <p className="empty-state">No patients found. Create one to get started.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Patient ID</th>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {data?.patients.map((patient: Patient) => (
                  <tr key={patient.id}>
                    <td>{patient.external_subject_id}</td>
                    <td>{patient.display_name}</td>
                    <td className="capitalize">{patient.subject_type}</td>
                    <td>{new Date(patient.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
