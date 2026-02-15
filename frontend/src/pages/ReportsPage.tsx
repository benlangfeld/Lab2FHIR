import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getReports, getPatients, uploadReport, generateBundle, downloadBundle, getParsedData } from '../services/api'
import type { Report } from '../types'
import './ReportsPage.css'

export default function ReportsPage() {
  const queryClient = useQueryClient()
  const [showUploadForm, setShowUploadForm] = useState(false)
  const [selectedPatientId, setSelectedPatientId] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null)

  const { data: patientsData } = useQuery({
    queryKey: ['patients'],
    queryFn: getPatients,
  })

  const { data: reportsData, isLoading, error } = useQuery({
    queryKey: ['reports'],
    queryFn: () => getReports(),
  })

  const { data: parsedData } = useQuery({
    queryKey: ['parsed-data', selectedReportId],
    queryFn: () => getParsedData(selectedReportId!),
    enabled: !!selectedReportId,
  })

  const uploadMutation = useMutation({
    mutationFn: ({ patientId, file }: { patientId: string; file: File }) =>
      uploadReport(patientId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      setShowUploadForm(false)
      setSelectedPatientId('')
      setSelectedFile(null)
    },
  })

  const generateMutation = useMutation({
    mutationFn: generateBundle,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedFile && selectedPatientId) {
      uploadMutation.mutate({ patientId: selectedPatientId, file: selectedFile })
    }
  }

  const handleGenerateBundle = async (reportId: string) => {
    await generateMutation.mutateAsync(reportId)
  }

  const handleDownloadBundle = async (reportId: string) => {
    const bundle = await downloadBundle(reportId)
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `bundle-${reportId}.json`
    a.click()
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      uploaded: '#6c757d',
      parsing: '#ffc107',
      review_pending: '#17a2b8',
      generating_bundle: '#fd7e14',
      completed: '#28a745',
      failed: '#dc3545',
      duplicate: '#6c757d',
    }
    return colors[status] || '#6c757d'
  }

  if (isLoading) return <div className="loading">Loading reports...</div>
  if (error) return <div className="error">Error loading reports: {(error as Error).message}</div>

  return (
    <div className="reports-page">
      <div className="page-header">
        <h1>Lab Reports</h1>
        <button className="btn btn-primary" onClick={() => setShowUploadForm(!showUploadForm)}>
          {showUploadForm ? 'Cancel' : 'Upload Report'}
        </button>
      </div>

      {showUploadForm && (
        <div className="form-card">
          <h2>Upload Lab Report</h2>
          <form onSubmit={handleUploadSubmit}>
            <div className="form-group">
              <label htmlFor="patient">Select Patient</label>
              <select
                id="patient"
                value={selectedPatientId}
                onChange={(e) => setSelectedPatientId(e.target.value)}
                required
              >
                <option value="">-- Select Patient --</option>
                {patientsData?.patients.map((patient) => (
                  <option key={patient.id} value={patient.id}>
                    {patient.display_name} ({patient.external_subject_id})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="file">PDF File</label>
              <input
                type="file"
                id="file"
                accept=".pdf"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={uploadMutation.isPending}>
              {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
            </button>

            {uploadMutation.isError && (
              <div className="error-message">
                Error: {(uploadMutation.error as { response?: { data?: { error?: { message?: string } } } }).response?.data?.error?.message || (uploadMutation.error as Error).message}
              </div>
            )}
          </form>
        </div>
      )}

      <div className="reports-list">
        {reportsData?.reports.length === 0 ? (
          <p className="empty-state">No reports found. Upload one to get started.</p>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reportsData?.reports.map((report: Report) => (
                  <tr key={report.id}>
                    <td>{report.original_filename}</td>
                    <td>
                      <span
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(report.status) }}
                      >
                        {report.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>{new Date(report.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className="actions">
                        {report.status === 'review_pending' && (
                          <>
                            <button
                              className="btn btn-small"
                              onClick={() => setSelectedReportId(report.id)}
                            >
                              View Data
                            </button>
                            <button
                              className="btn btn-small btn-success"
                              onClick={() => handleGenerateBundle(report.id)}
                              disabled={generateMutation.isPending}
                            >
                              Generate Bundle
                            </button>
                          </>
                        )}
                        {report.status === 'completed' && (
                          <button
                            className="btn btn-small btn-success"
                            onClick={() => handleDownloadBundle(report.id)}
                          >
                            Download Bundle
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedReportId && parsedData && (
        <div className="modal-overlay" onClick={() => setSelectedReportId(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Parsed Data</h2>
              <button className="close-btn" onClick={() => setSelectedReportId(null)}>
                ×
              </button>
            </div>
            <div className="modal-body">
              <pre>{JSON.stringify(parsedData.payload, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
