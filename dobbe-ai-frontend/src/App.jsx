import React, { useState } from "react";
import ImagePanel from "./components/ImagePanel";
import Navbar from "./components/Navabr";
import ReportPanel from "./components/ReportPanel";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleResult = (data) => {
    setResult(data);
    if (data?.original_image_b64) {
      const imageUrl = `data:image/png;base64,${data.original_image_b64}`;
      setPreviewUrl(imageUrl);
    } else {
      console.warn("⚠️ original_image_b64 not found in API response");
    }
  };

  return (
    <div className="app">
      <Navbar />
      <div className="left">
        <ImagePanel onResult={handleResult} previewUrl={previewUrl} />
      </div>
      <div className="right">
        <ReportPanel report={result?.diagnostic_report} />
      </div>
    </div>
  );
}

export default App;
