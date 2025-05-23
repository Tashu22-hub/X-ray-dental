import React from "react";
import jsPDF from "jspdf";
import "./ReportPanel.css";

const ReportPanel = ({ report }) => {
  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("🦷 Dental X-Ray Diagnostic Report", 10, 20);

    doc.setFontSize(12);
    const lines = doc.splitTextToSize(report, 180); // auto-wrap long text
    doc.text(lines, 10, 40);

    doc.save("dental_report.pdf");
  };

  return (
    <div className="report-panel">
      <h2>📋 Diagnostic Report</h2>
      <div className="report-text">
        {report ? (
          <>
            <p>{report}</p>
            <button onClick={handleDownloadPDF} className="download-btn">
              📥 Download PDF
            </button>
          </>
        ) : (
          <p className="placeholder">
            Upload an image and click Predict to view report.
          </p>
        )}
      </div>
    </div>
  );
};

export default ReportPanel;
