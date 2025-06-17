import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useRef } from 'react';
import html2canvas from 'html2canvas';
import axios from 'axios';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function ReportViewer({ report }) {
  const chartRef = useRef(null);

  const chartData = {
    labels: ['Cyclomatic Complexity', 'Code Smells', 'Maintainability Index'],
    datasets: [
      {
        label: 'Code Metrics',
        data: [report.complexity, report.smells, report.maintainability],
        backgroundColor: ['#36A2EB', '#FF6384', '#4BC0C0'],
        borderColor: ['#2A80B9', '#CC4B37', '#3CA8A8'],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Code Quality Metrics' },
    },
    scales: {
      y: { beginAtZero: true },
    },
  };

  const handleDownloadPDF = async () => {
    try {
      // Capture chart as base64
      const canvas = await html2canvas(chartRef.current);
      const chartImage = canvas.toDataURL('image/png');

      // Prepare data for PDF
      const pdfData = {
        filename: report.filename,
        complexity: report.complexity,
        smells: report.smells,
        maintainability: report.maintainability,
        smell_details: report.smell_details || [],
        chart_image: chartImage,
      };

      // Send to backend
      const response = await axios.post('http://localhost:8000/generate_pdf', pdfData, {
        responseType: 'blob',
      });

      // Trigger download
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${report.filename}_analysis.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('PDF download error:', error);
      alert('Failed to download PDF: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="mt-5">
      <h3 className="mb-3">Analysis Report for {report.filename}</h3>
      <div className="card p-3 mb-3" ref={chartRef}>
        <Bar data={chartData} options={options} />
      </div>
      <div className="card p-3">
        <h5>Details:</h5>
        <ul className="list-group list-group-flush">
          <li className="list-group-item">Complexity: {report.complexity}</li>
          <li className="list-group-item">Code Smells: {report.smells} issues</li>
          <li className="list-group-item">Maintainability Index: {report.maintainability.toFixed(1)}</li>
        </ul>
        {report.smell_details && report.smell_details.length > 0 ? (
          <div className="accordion mt-3" id="smellAccordion">
            {report.smell_details.map((smell, index) => (
              <div className="accordion-item" key={index}>
                <h2 className="accordion-header">
                  <button
                    className="accordion-button collapsed"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target={`#collapse${index}`}
                  >
                    Smell {index + 1}: {smell.message}
                  </button>
                </h2>
                <div
                  id={`collapse${index}`}
                  className="accordion-collapse collapse"
                  data-bs-parent="#smellAccordion"
                >
                  <div className="accordion-body">
                    <strong>Type:</strong> {smell.type}<br />
                    <strong>Line:</strong> {smell.line}<br />
                    <strong>Message:</strong> {smell.message}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-3 text-muted">No code smells detected.</p>
        )}
        <button className="btn btn-primary mt-3" onClick={handleDownloadPDF}>
          Download PDF Report
        </button>
      </div>
    </div>
  );
}

export default ReportViewer;