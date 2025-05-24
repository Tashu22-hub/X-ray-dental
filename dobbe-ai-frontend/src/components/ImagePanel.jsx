import React, { useState } from "react";
import "./ImagePanel.css";

const ImagePanel = ({ onResult, previewUrl, setIsLoading }) => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    onResult(null); // clear preview and report
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a DICOM (.dcm/.rvg) file.");

    const formData = new FormData();
    formData.append("file", file);

    setIsLoading(true); // use global spinner
    try {
      const res = await fetch("https://x-ray-dental-backned.onrender.com/upload-dicom/", {
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
      setIsLoading(false); // stop global spinner 
    }
  };

  return (
    <div className="image-panel">
      <h2>🦷 Dental X-Ray Uploader</h2>
      <input type="file" accept=".dcm,.rvg" multiple onChange={handleFileChange} />
      <button onClick={handleUpload}>
        Predict
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
