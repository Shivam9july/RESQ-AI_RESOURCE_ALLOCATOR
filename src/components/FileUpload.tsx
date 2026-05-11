import React, { useState } from "react";

interface UploadResponse {
  id: number;
  incident_type: string;
  confidence: number;
  severity: string;
  latitude: number | null;
  longitude: number | null;
  detected_at: string;
  image_file: string | null;
  video_file: string | null;
  image_url: string | null;
  video_url: string | null;
  estimated_affected_area: number | null;
  estimated_affected_population: number | null;
  relief_amount: string | null;
  meta: Record<string, any>;
}

interface Props {
  apiBase: string;
  onUploadComplete?: (response: UploadResponse) => void;
}

const formatFileSize = (bytes: number) =>
  `${(bytes / (1024 * 1024)).toFixed(2)} MB`;

const titleCase = (value: string | null | undefined) =>
  value ? value.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()) : "--";

export const FileUpload: React.FC<Props> = ({ apiBase, onUploadComplete }) => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [latitude, setLatitude] = useState<string>("");
  const [longitude, setLongitude] = useState<string>("");
  const [incidentType, setIncidentType] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadResponse | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0]);
      setVideoFile(null);
      setError(null);
    }
  };

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setVideoFile(e.target.files[0]);
      setImageFile(null);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!imageFile && !videoFile) {
      setError("Please select an image or video file.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();

      if (imageFile) {
        formData.append("image", imageFile);
      }
      if (videoFile) {
        formData.append("video", videoFile);
      }
      if (latitude) {
        formData.append("latitude", latitude);
      }
      if (longitude) {
        formData.append("longitude", longitude);
      }
      if (incidentType) {
        formData.append("incident_type", incidentType);
      }

      const response = await fetch(`${apiBase}/detect/upload/`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error ${response.status}`);
      }

      const data: UploadResponse = await response.json();
      setResult(data);
      onUploadComplete?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
      console.error("Upload error:", err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: string | null) => {
    if (!amount) return "--";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(parseFloat(amount));
  };

  return (
    <section className="panel upload-panel">
      <div className="section-heading">
        <span className="eyebrow">Incident intake</span>
        <h2>Upload Disaster Media</h2>
        <p>
          Submit field media with optional coordinates to generate an incident
          record and relief estimate.
        </p>
      </div>

      <form className="upload-form" onSubmit={handleSubmit}>
        <div className="media-picker-grid">
          <label className={`upload-zone ${imageFile ? "selected" : ""}`} htmlFor="image-upload">
            <span className="upload-zone-title">Image File</span>
            <span className="upload-zone-copy">
              {imageFile ? imageFile.name : "Choose JPG, PNG, or WebP"}
            </span>
            {imageFile && (
              <span className="file-size">{formatFileSize(imageFile.size)}</span>
            )}
            <input
              id="image-upload"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              disabled={loading}
            />
          </label>

          <label className={`upload-zone ${videoFile ? "selected" : ""}`} htmlFor="video-upload">
            <span className="upload-zone-title">Video File</span>
            <span className="upload-zone-copy">
              {videoFile ? videoFile.name : "Choose MP4, MOV, or AVI"}
            </span>
            {videoFile && (
              <span className="file-size">{formatFileSize(videoFile.size)}</span>
            )}
            <input
              id="video-upload"
              type="file"
              accept="video/*"
              onChange={handleVideoChange}
              disabled={loading}
            />
          </label>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="latitude">Latitude</label>
            <input
              id="latitude"
              type="number"
              step="any"
              placeholder="28.6139"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="longitude">Longitude</label>
            <input
              id="longitude"
              type="number"
              step="any"
              placeholder="77.2090"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="incident-type">Disaster Type</label>
          <select
            id="incident-type"
            value={incidentType}
            onChange={(e) => setIncidentType(e.target.value)}
            disabled={loading}
          >
            <option value="">Auto-detect</option>
            <option value="fire">Fire</option>
            <option value="flood">Flood</option>
            <option value="crowd">Crowd / Social Distance</option>
          </select>
        </div>

        {error && <div className="alert error-message">{error}</div>}

        <button
          type="submit"
          className="button primary"
          disabled={loading || (!imageFile && !videoFile)}
        >
          {loading ? "Analyzing media" : "Analyze Disaster"}
        </button>
      </form>

      {result && (
        <div className="result-panel">
          <div className="result-header">
            <div>
              <span className="eyebrow">Detection results</span>
              <h3>{titleCase(result.incident_type)}</h3>
            </div>
            <span className={`severity-badge severity-${result.severity}`}>
              {titleCase(result.severity)}
            </span>
          </div>

          <div className="result-grid">
            <div className="result-item">
              <span className="result-label">Confidence</span>
              <span className="result-value">
                {(result.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Affected Area</span>
              <span className="result-value">
                {result.estimated_affected_area
                  ? `${result.estimated_affected_area.toFixed(2)} km2`
                  : "--"}
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Affected Population</span>
              <span className="result-value">
                {result.estimated_affected_population
                  ? result.estimated_affected_population.toLocaleString()
                  : "--"}
              </span>
            </div>
            <div className="result-item relief-card">
              <span className="result-label">Relief Amount</span>
              <span className="result-value relief-amount">
                {formatCurrency(result.relief_amount)}
              </span>
            </div>
          </div>

          {(result.image_url || result.video_url) && (
            <div className="media-preview">
              <h4>Uploaded Media</h4>
              {result.image_url && (
                <img
                  src={result.image_url}
                  alt="Uploaded disaster"
                  className="preview-image"
                />
              )}
              {result.video_url && (
                <video src={result.video_url} controls className="preview-video">
                  Your browser does not support video playback.
                </video>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  );
};
