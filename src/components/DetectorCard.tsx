import React, { useState } from "react";
import type { DetectorType } from "../App";

interface Props {
  title: string;
  type: DetectorType;
  placeholder: string;
  loading: boolean;
  onTrigger: (type: DetectorType, videoPath: string) => Promise<void>;
}

const detectorMeta: Record<DetectorType, { tone: string; description: string }> = {
  fire: {
    tone: "fire",
    description: "Smoke, flame, and urban fire indicators",
  },
  flood: {
    tone: "flood",
    description: "Water logging and inundation signals",
  },
  "social-distance": {
    tone: "crowd",
    description: "Crowd density and spacing violations",
  },
};

export const DetectorCard: React.FC<Props> = ({
  title,
  type,
  placeholder,
  loading,
  onTrigger,
}) => {
  const [videoPath, setVideoPath] = useState("");
  const meta = detectorMeta[type];

  async function handleClick() {
    if (!videoPath) return;
    await onTrigger(type, videoPath);
  }

  return (
    <article className={`detector-card ${meta.tone}`}>
      <div className="detector-topline">
        <span className="detector-icon" aria-hidden="true" />
        <div>
          <h3>{title}</h3>
          <p>{meta.description}</p>
        </div>
      </div>

      <label className="field-label" htmlFor={`${type}-path`}>
        Video source path
      </label>
      <input
        id={`${type}-path`}
        type="text"
        className="input"
        placeholder={placeholder}
        value={videoPath}
        onChange={(e) => setVideoPath(e.target.value)}
      />
      <button
        className="button block"
        disabled={loading || !videoPath}
        onClick={handleClick}
      >
        {loading ? "Running analysis" : "Run Detector"}
      </button>
    </article>
  );
};
