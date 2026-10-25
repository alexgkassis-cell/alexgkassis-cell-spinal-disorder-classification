"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  Activity, ArrowRight, ArrowUpRight, Check, CheckCircle2, ChevronRight,
  CircleAlert, Database, FileImage, Github, Info, Layers3, LockKeyhole,
  RotateCcw, ScanLine, ShieldCheck, SlidersHorizontal, UploadCloud, X,
} from "lucide-react";

type Health = "checking" | "ready" | "offline";
type Predictions = {
  label: string;
  scores: Record<string, number>;
  preprocessing: string;
  model: string;
  research_only: true;
  notice: string;
};
const categories = ["Normal", "Scoliosis", "Spondylolisthesis"] as const;
const MAX_BYTES = 4 * 1024 * 1024;
const repoUrl = "https://github.com/alexgkassis-cell/alexgkassis-cell-spinal-disorder-classification";

function Emblem({ className = "" }: { className?: string }) {
  return <span className={`emblem ${className}`} aria-hidden="true"><span/><span/><span/><span/></span>;
}

function SpineVisualization() {
  return (
    <div className="viz-card" aria-label="Conceptual spinal alignment visualization, not an actual medical scan" role="img">
      <div className="viz-grid" aria-hidden="true" />
      <div className="viz-hud viz-hud-left">FIG 01. / RESEARCH VIEW</div>
      <div className="viz-hud viz-hud-right"><span className="tiny-pulse"/> ANALYSIS READY</div>
      <svg className="spine-svg" viewBox="0 0 360 460" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <linearGradient id="spine" x1="95" y1="70" x2="253" y2="403" gradientUnits="userSpaceOnUse">
            <stop stopColor="#C7FAE9"/><stop offset="0.5" stopColor="#7BDCC8"/><stop offset="1" stopColor="#3E9DB3"/>
          </linearGradient>
          <linearGradient id="torso" x1="80" y1="60" x2="305" y2="410" gradientUnits="userSpaceOnUse">
            <stop stopColor="#47C5AE" stopOpacity="0.17"/><stop offset="1" stopColor="#47C5AE" stopOpacity="0"/>
          </linearGradient>
          <filter id="glow"><feGaussianBlur stdDeviation="17"/></filter>
        </defs>
        <path d="M179 53C128 81 128 143 164 191C205 243 213 284 177 335C153 372 169 404 192 426" stroke="#4CDDBE" strokeWidth="46" opacity=".17" filter="url(#glow)"/>
        <path d="M186 45C123 68 114 159 166 220C202 261 207 314 171 353C157 375 172 409 192 423" stroke="url(#torso)" strokeWidth="100" strokeLinecap="round"/>
        <path d="M176 59C140 90 135 135 160 181C174 206 189 226 192 254C197 301 169 323 167 354C164 382 177 405 196 426" stroke="#A4F7DE" strokeWidth="2" strokeDasharray="5 9" opacity=".67"/>
        {Array.from({ length: 15 }, (_, i) => {
          const t = i / 14;
          const y = 68 + t * 323;
          const x = 169 + 21 * Math.sin(t * Math.PI * 2.3) - 8 * t;
          const rot = -20 + 42 * Math.sin(t * Math.PI * 1.7);
          const width = 40 + t * 14;
          return <g key={i} transform={`translate(${x} ${y}) rotate(${rot})`}>
            <rect x={-width/2} y="-12" width={width} height="21" rx="6" fill="#88EDCE" fillOpacity={0.17 + t * .08} stroke="url(#spine)" strokeOpacity=".84" strokeWidth="1.7"/>
            <path d={`M${-width/2+8} -4H${width/2-8}`} stroke="#DBFFF2" strokeOpacity=".55" strokeWidth="1.3"/>
            <path d={`M${-width/2+10} 5H${width/2-10}`} stroke="#56D1BF" strokeOpacity=".5" strokeWidth="1"/>
          </g>;
        })}
        <path d="M73 152H108M252 284H292" stroke="#81E9D1" strokeOpacity=".65" strokeWidth="1.4"/>
        <circle cx="109" cy="152" r="3.7" fill="#85F5D4"/>
        <circle cx="250" cy="284" r="3.7" fill="#85F5D4"/>
        <rect x="26" y="127" width="63" height="44" rx="7" fill="#152B3C" stroke="#31546A"/>
        <text x="38" y="145" fill="#91ABBA" fontSize="9" letterSpacing="1">SCAN</text>
        <text x="38" y="160" fill="#A9F3DF" fontSize="12" fontWeight="600">01 / 03</text>
        <rect x="265" y="264" width="78" height="45" rx="7" fill="#152B3C" stroke="#31546A"/>
        <text x="278" y="282" fill="#91ABBA" fontSize="9" letterSpacing="1">INPUT</text>
        <text x="278" y="297" fill="#A9F3DF" fontSize="12" fontWeight="600">128 × 128</text>
      </svg>
      <div className="viz-bottom"><span>CONCEPTUAL MODEL VISUALIZATION</span><span>NOT A PATIENT IMAGE</span></div>
    </div>
  );
}

export default function Home() {
  const [health, setHealth] = useState<Health>("checking");
  const [selected, setSelected] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [hasPermission, setHasPermission] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Predictions | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const refreshHealth = useCallback(async () => {
    setHealth("checking");
    try {
      const response = await fetch("/api/health", { cache: "no-store" });
      const json = await response.json();
      setHealth(response.ok && json.model_loaded === true ? "ready" : "offline");
    } catch { setHealth("offline"); }
  }, []);

  useEffect(() => { void refreshHealth(); }, [refreshHealth]);
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  function chooseFile(file?: File) {
    setError(null);
    setResult(null);
    if (!file) return;
    if (!["image/jpeg", "image/png"].includes(file.type)) {
      setError("Please select an actual JPEG or PNG X-ray image.");
      return;
    }
    if (!file.size || file.size > MAX_BYTES) {
      setError("Image size must be smaller than 4 MiB.");
      return;
    }
    setSelected(file);
    setPreview(URL.createObjectURL(file));
    setHasPermission(false);
  }

  function clearFile() {
    setSelected(null);
    setPreview(null);
    setResult(null);
    setError(null);
    setHasPermission(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function analyze() {
    if (!selected || !hasPermission || pending) return;
    if (health !== "ready") {
      setError("The research model is offline. Configure and start the private Python inference server first.");
      return;
    }
    setError(null);
    setResult(null);
    setPending(true);
    try {
      const form = new FormData();
      form.set("file", selected, selected.type === "image/png" ? "upload.png" : "upload.jpg");
      const response = await fetch("/api/predict", { method: "POST", body: form, cache: "no-store" });
      const json = await response.json();
      if (!response.ok) throw new Error(typeof json.detail === "string" ? json.detail : "Prediction failed");
      if (!json.scores || !categories.every((c) => typeof json.scores[c] === "number")) {
        throw new Error("The model returned an unexpected result.");
      }
      setResult(json as Predictions);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Unable to analyze image");
      await refreshHealth();
    } finally { setPending(false); }
  }

  return (
    <div className="site-shell">
      <div className="background-orb orb-one" aria-hidden="true" />
      <div className="background-orb orb-two" aria-hidden="true" />
      <header className="site-header container">
        <a className="brand" href="#top" aria-label="SpineLab home"><Emblem/><span>spine<span className="brand-accent">lab</span><span className="brand-period">.</span></span></a>
        <nav aria-label="Main navigation" className="desktop-nav">
          <a href="#workspace">Classifier</a><a href="#method">Methodology</a><a href="#research">Research results</a>
        </nav>
        <a className="github-link" href={repoUrl} target="_blank" rel="noopener noreferrer"><Github size={17}/><span>View GitHub</span><ArrowUpRight size={15}/></a>
      </header>

      <main id="top">
        <div className="container">
          <div className="top-announcement"><span className="announce-icon"><Activity size={14}/></span><span>AN EXPERIMENTAL CLASSIFICATION WORKSPACE</span><span className="announce-divider"/><span className="announce-secondary">Research only · Not a diagnostic tool</span></div>
          <section className="hero" aria-labelledby="hero-heading">
            <div className="hero-copy">
              <div className="eyebrow"><span className="eyebrow-line"/> THE NEXT DIMENSION OF IMAGE ANALYSIS</div>
              <h1 id="hero-heading">A closer look<br/>at the <span className="gradient-text">spine.</span></h1>
              <p className="hero-description">An interactive research platform exploring how deep learning classifies spinal X-rays across three categories.</p>
              <div className="hero-actions"><a href="#workspace" className="primary-cta">Try the classifier <ArrowRight size={18}/></a><a href="#method" className="text-cta">Explore the methodology <ChevronRight size={17}/></a></div>
              <div className="hero-footnote"><ShieldCheck size={18}/><span>Built on a frozen, held-out research evaluation.</span></div>
            </div>
            <SpineVisualization/>
          </section>

          <section className="stat-strip" aria-label="Model research metrics">
            <div className="stat-item"><div className="stat-label">FINAL TEST ACCURACY <Info size={13}/></div><div className="stat-number">92.16<span>%</span></div><div className="stat-note">47 of 51 held-out images</div></div>
            <div className="stat-rule"/>
            <div className="stat-item"><div className="stat-label">VALIDATION ACCURACY <Info size={13}/></div><div className="stat-number">96.15<span>%</span></div><div className="stat-note">Used for model selection</div></div>
            <div className="stat-rule"/>
            <div className="stat-item"><div className="stat-label">CLASSIFICATION TASK</div><div className="stat-number stat-number-small">03<span> classes</span></div><div className="stat-note">Normal · Scoliosis · Spondylolisthesis</div></div>
          </section>
        </div>

        <section className="workspace-section" id="workspace">
          <div className="container workspace-grid">
            <aside className="workspace-aside">
              <div className="section-index"><span>01</span> / EXPERIMENTAL CLASSIFIER</div>
              <h2>Image in.<br/><span>Insight out.</span></h2>
              <p>See how our frozen CNN analyzes an X-ray. Authorized images are sent to the inference server for processing. This application does not intentionally save uploads, but hosting providers may process request data. Remove identifying information before uploading.</p>
              <div className={`service-pill ${health === "ready" ? "online" : health === "checking" ? "checking" : "offline"}`}>
                <span className="service-dot"/><span>{health === "ready" ? "Inference model connected" : health === "checking" ? "Checking model connection" : "Inference model not connected"}</span>
                <button type="button" onClick={refreshHealth} title="Check model connection" aria-label="Refresh model connection" className="refresh-button"><RotateCcw size={14}/></button>
              </div>
              <div className="aside-note"><LockKeyhole size={17}/><span>The C08 model remains on a private inference server, not in this public repository. Upload only appropriately authorized, de-identified images.</span></div>
            </aside>

            <div className="classifier-panel">
              <div className="panel-heading"><div className="panel-title"><span className="panel-icon"><ScanLine size={19}/></span><div><h3>Analyze a radiograph</h3><p>Upload a spinal X-ray to begin</p></div></div><span className="panel-tag">C08 / v1.0</span></div>
              <div className="panel-body">
                <input ref={fileInputRef} className="sr-only" id="xray-input" type="file" accept="image/jpeg,image/png,.jpg,.jpeg,.png" onChange={event => chooseFile(event.currentTarget.files?.[0])}/>
                {!selected ? (
                  <div className={`drop-zone ${isDragging ? "dragging" : ""}`} role="button" tabIndex={0}
                    onKeyDown={event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); fileInputRef.current?.click(); } }}
                    onClick={() => fileInputRef.current?.click()}
                    onDragEnter={event => { event.preventDefault(); setIsDragging(true); }}
                    onDragOver={event => { event.preventDefault(); setIsDragging(true); }}
                    onDragLeave={event => { event.preventDefault(); setIsDragging(false); }}
                    onDrop={event => { event.preventDefault(); setIsDragging(false); chooseFile(event.dataTransfer.files[0]); }}>
                    <div className="upload-icon"><UploadCloud size={27} strokeWidth={1.65}/></div>
                    <h4>Drop your X-ray here</h4><p>or <span>browse files</span> from your device</p>
                    <div className="upload-meta"><span>JPEG or PNG</span><span className="meta-point"/><span>Maximum 4 MiB</span></div>
                  </div>
                ) : (
                  <div className="uploaded-box">
                    <div className="image-preview"><img src={preview || ""} alt="Local preview of the X-ray selected for analysis"/></div>
                    <div className="file-info"><span className="file-icon"><FileImage size={21}/></span><div><strong>{selected.name}</strong><span>{(selected.size / (1024 * 1024)).toFixed(2)} MiB · Ready for analysis</span></div><button type="button" onClick={clearFile} aria-label="Remove selected image" disabled={pending}><X size={18}/></button></div>
                  </div>
                )}
                <label className="permission-row"><input type="checkbox" checked={hasPermission} onChange={event => setHasPermission(event.target.checked)} /><span>I own or have permission to submit this de-identified image for server-side processing. I understand the output is <strong>not medical advice</strong>.</span></label>
                {error && <div role="alert" className="error-message"><CircleAlert size={18}/><span>{error}</span></div>}
                <button className="analyze-button" type="button" disabled={!selected || !hasPermission || pending || health !== "ready"} onClick={analyze}>
                  {pending ? <><span className="loading-spinner"/> Analyzing image…</> : <><ScanLine size={18}/> Run research analysis <ArrowRight size={17}/></>}
                </button>
                <p className="panel-hint">Research demonstration · No intentional image storage · Do not upload identifiable patient data</p>
              </div>

              {result && (
                <div className="analysis-output" aria-live="polite">
                  <div className="output-heading"><span className="result-state"><CheckCircle2 size={16}/> Analysis complete</span><span className="output-secondary">RESEARCH RESULT</span></div>
                  <div className="top-prediction"><span>Highest model score</span><h4>{result.label}</h4><p>This is a model-generated category, not a diagnosis.</p></div>
                  <div className="score-list">{categories.map((cat) => {
                    const v = Math.min(1, Math.max(0, result.scores[cat] ?? 0));
                    return <div className="score-row" key={cat}><div className="score-title"><span>{cat}</span><strong>{(v * 100).toFixed(1)}%</strong></div><div className="score-track"><div className={cat === result.label ? "score-fill selected" : "score-fill"} style={{ width: `${v * 100}%` }}/></div></div>;
                  })}</div>
                  <div className="result-disclaimer"><Info size={17}/><span>Scores are not calibrated probabilities and must not guide medical decisions. Dataset patient independence is unverified.</span></div>
                </div>
              )}
            </div>
          </div>
        </section>

        <section id="method" className="method-section container">
          <div className="section-heading"><div><div className="section-index"><span>02</span> / THE PIPELINE</div><h2>Built with intention.<br/><span>Tested with rigor.</span></h2></div><p>One locked model. One consistent preprocessing path. No tuning against the final test set.</p></div>
          <div className="method-cards">
            <article className="method-card"><div className="method-top"><span className="step-number">01</span><FileImage size={23}/></div><h3>Image preparation</h3><p>Resize with LANCZOS padding, convert to grayscale, and normalize to 128 × 128 pixels.</p><span className="method-tag">INPUT: 128 × 128 × 1</span></article>
            <article className="method-card"><div className="method-top"><span className="step-number">02</span><SlidersHorizontal size={23}/></div><h3>Local contrast</h3><p>Apply contrast-limited adaptive histogram equalization to an 8 × 8 tile grid.</p><span className="method-tag">CLAHE: CLIP 3.0 / 64 TILES</span></article>
            <article className="method-card"><div className="method-top"><span className="step-number">03</span><Layers3 size={23}/></div><h3>CNN inference</h3><p>Feed the processed image through the locked reference convolutional neural network.</p><span className="method-tag">C08 · TRAINING SEED 456</span></article>
          </div>
        </section>

        <section id="research" className="research-section"><div className="container research-grid">
          <div><div className="section-index"><span>03</span> / RESEARCH OUTCOMES</div><h2>Research<br/>results.</h2><p>Our model was selected on a 52-image validation split, then evaluated once on 51 held-out X-rays. No further model selection was performed after the test.</p><a href={repoUrl} rel="noopener noreferrer" target="_blank" className="research-link">Read the full research <ArrowUpRight size={17}/></a></div>
          <div className="research-table"><div className="research-table-title"><Database size={18}/> LOCKED EVALUATION</div><div className="comparison-row comparison-header"><span>METRIC</span><span>VALIDATION</span><span>FINAL TEST</span></div><div className="comparison-row"><span>Images</span><strong>52</strong><strong>51</strong></div><div className="comparison-row"><span>Accuracy</span><strong>96.15%</strong><strong>92.16%</strong></div><div className="comparison-row"><span>Macro F1</span><strong>0.9528</strong><strong>0.9152</strong></div><div className="comparison-row"><span>Balanced accuracy</span><strong>96.03%</strong><strong>91.56%</strong></div><div className="table-footnote"><CircleAlert size={15}/><span>Only 338 source images; patient-disjointness not confirmed. Not validated for clinical use.</span></div></div>
        </div></section>
      </main>
      <footer className="site-footer container"><div className="footer-brand"><Emblem/> spine<span>lab.</span></div><p>Spinal X-ray classification research · For educational exploration only</p><a href={repoUrl} target="_blank" rel="noopener noreferrer">Source code <ArrowUpRight size={15}/></a></footer>
    </div>
  );
}
