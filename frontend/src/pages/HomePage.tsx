import './HomePage.css'

export default function HomePage() {
  return (
    <div className="home-page">
      <div className="hero">
        <h1>Lab PDF to FHIR Converter</h1>
        <p className="subtitle">
          Convert laboratory PDF reports into FHIR R4 resources with ease
        </p>
      </div>

      <div className="features">
        <div className="feature-card">
          <h2>📄 Upload PDFs</h2>
          <p>Upload text-based laboratory reports in PDF format</p>
        </div>

        <div className="feature-card">
          <h2>🔄 Automatic Processing</h2>
          <p>Automatic text extraction and parsing to structured format</p>
        </div>

        <div className="feature-card">
          <h2>🏥 FHIR R4 Bundles</h2>
          <p>Generate standards-compliant FHIR bundles ready for upload</p>
        </div>

        <div className="feature-card">
          <h2>✅ Duplicate Detection</h2>
          <p>Automatic detection of duplicate uploads using file hashing</p>
        </div>
      </div>

      <div className="getting-started">
        <h2>Getting Started</h2>
        <ol>
          <li>Create a patient profile in the <strong>Patients</strong> section</li>
          <li>Upload a lab report PDF in the <strong>Reports</strong> section</li>
          <li>Review the parsed data and generate FHIR bundle</li>
          <li>Download the bundle and upload to your FHIR server</li>
        </ol>
      </div>
    </div>
  )
}
