import { useState } from 'react';
import UploadForm from './components/UploadForm';
import ReportViewer from './components/ReportViewer';
import './App.css';

function App() {
  const [report, setReport] = useState(null);

  return (
    <div className="container mt-5">
      <h1 className="text-center mb-4">Code Quality Analyzer</h1>
      <UploadForm setReport={setReport} />
      {report && <ReportViewer report={report} />}
    </div>
  );
}

export default App;