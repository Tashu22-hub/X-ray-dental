import React, { useState } from "react";
import "./ImagePanel.css";

const ImagePanel = ({ onResult, previewUrl }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    onResult(null); // clear preview and report
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a DICOM (.dcm/.rvg) file.");

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/upload-dicom/", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");

      onResult(data);
    } catch (err) {
      console.error("❌ Upload error:", err);
      alert(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="image-panel">
      <h2>🦷 Dental X-Ray Uploader</h2>
      <input type="file"  accept=".dcm,.rvg" multiple onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Analyzing..." : "Predict"}
      </button>
      {previewUrl && (
        <img
          className="preview-image"
          src={previewUrl}
          alt="X-Ray Preview"
          style={{ maxWidth: "100%", marginTop: "1rem" }}
        />
      )}
    </div>
  );
};

export default ImagePanel;
 