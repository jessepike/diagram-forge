"use client";

import { useState, useRef } from "react";
import type { Template, UIState, InputTab } from "@/app/page";
import TemplateCard from "./TemplateCard";

interface LeftPanelProps {
  templates: Template[];
  selectedTemplate: string | null;
  onSelectTemplate: (id: string) => void;
  contentInput: string;
  onContentChange: (value: string) => void;
  inputTab: InputTab;
  onTabChange: (tab: InputTab) => void;
  provider: string;
  onProviderChange: (value: string) => void;
  onGenerate: () => void;
  onOpenSettings: () => void;
  uiState: UIState;
}

export default function LeftPanel({
  templates,
  selectedTemplate,
  onSelectTemplate,
  contentInput,
  onContentChange,
  inputTab,
  onTabChange,
  provider,
  onProviderChange,
  onGenerate,
  onOpenSettings,
  uiState,
}: LeftPanelProps) {
  const [uploadStatus, setUploadStatus] = useState<
    "idle" | "uploading" | "done" | "error"
  >("idle");
  const [uploadFilename, setUploadFilename] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFileUpload(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    setUploadStatus("uploading");
    setUploadFilename(file.name);
    setUploadError(null);

    try {
      const res = await fetch("/api/extract", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail ?? `Upload failed (${res.status})`);
      }
      const data = await res.json();
      onContentChange(data.text);
      setUploadStatus("done");
      onTabChange("paste");
    } catch (err: unknown) {
      setUploadStatus("error");
      setUploadError(
        err instanceof Error ? err.message : "Upload failed"
      );
    }
  }

  function clearUpload() {
    setUploadStatus("idle");
    setUploadFilename(null);
    setUploadError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  return (
    <div className="w-[400px] min-w-[400px] bg-white border-r border-slate-200 flex flex-col h-full">
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-5 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="material-symbols-outlined text-white text-lg">
              hub
            </span>
          </div>
          <span className="font-bold text-slate-900">Diagram Forge</span>
        </div>
        <button
          onClick={onOpenSettings}
          className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
        >
          <span className="material-symbols-outlined text-xl">settings</span>
        </button>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {/* Templates */}
        <div>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Templates
          </h3>
          <div className="space-y-1">
            {templates.map((t) => (
              <TemplateCard
                key={t.id}
                id={t.id}
                name={t.name}
                description={t.description}
                isActive={selectedTemplate === t.id}
                onClick={() => onSelectTemplate(t.id)}
              />
            ))}
          </div>
        </div>

        <hr className="border-slate-200" />

        {/* Input */}
        <div>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Input
          </h3>

          {/* Tab switcher */}
          <div className="flex gap-1 bg-slate-100 rounded-lg p-1 mb-4">
            <button
              onClick={() => onTabChange("paste")}
              className={`flex-1 text-sm font-medium py-1.5 rounded-md transition-colors ${
                inputTab === "paste"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              Paste
            </button>
            <button
              onClick={() => onTabChange("upload")}
              className={`flex-1 text-sm font-medium py-1.5 rounded-md transition-colors ${
                inputTab === "upload"
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              Upload
            </button>
          </div>

          {inputTab === "paste" ? (
            <textarea
              value={contentInput}
              onChange={(e) => onContentChange(e.target.value)}
              placeholder="Paste your architecture description, API spec, or system design here..."
              className="w-full h-32 p-3 text-sm border border-slate-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary placeholder:text-slate-400"
            />
          ) : (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.md"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileUpload(file);
                }}
              />

              {uploadStatus === "idle" && (
                <div
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setIsDragOver(true);
                  }}
                  onDragLeave={() => setIsDragOver(false)}
                  onDrop={(e) => {
                    e.preventDefault();
                    setIsDragOver(false);
                    const file = e.dataTransfer.files[0];
                    if (file) handleFileUpload(file);
                  }}
                  className={`w-full h-32 border-2 border-dashed rounded-lg flex flex-col items-center justify-center text-sm cursor-pointer transition-colors ${
                    isDragOver
                      ? "border-primary bg-primary/5 text-primary"
                      : "border-slate-300 text-slate-400 hover:border-slate-400 hover:text-slate-500"
                  }`}
                >
                  <span className="material-symbols-outlined text-2xl mb-1">
                    upload_file
                  </span>
                  <span>Browse or drag a file here</span>
                  <span className="text-xs mt-1">.pdf, .docx, .md</span>
                </div>
              )}

              {uploadStatus === "uploading" && (
                <div className="w-full h-32 border-2 border-dashed border-primary/40 rounded-lg flex flex-col items-center justify-center text-sm text-primary">
                  <span className="material-symbols-outlined text-2xl mb-1 animate-spin">
                    progress_activity
                  </span>
                  <span>Extracting {uploadFilename}...</span>
                </div>
              )}

              {uploadStatus === "done" && (
                <div className="w-full h-32 border-2 border-dashed border-green-300 bg-green-50 rounded-lg flex flex-col items-center justify-center text-sm text-green-700 gap-2">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-lg">
                      check_circle
                    </span>
                    <span className="font-medium">{uploadFilename}</span>
                  </div>
                  <span className="text-xs text-green-600">
                    {contentInput.length.toLocaleString()} chars extracted
                  </span>
                  <button
                    onClick={clearUpload}
                    className="text-xs text-green-600 underline hover:text-green-800"
                  >
                    Clear
                  </button>
                </div>
              )}

              {uploadStatus === "error" && (
                <div className="w-full h-32 border-2 border-dashed border-red-300 bg-red-50 rounded-lg flex flex-col items-center justify-center text-sm text-red-600 gap-2">
                  <span className="material-symbols-outlined text-2xl">
                    error
                  </span>
                  <span>{uploadError}</span>
                  <button
                    onClick={clearUpload}
                    className="text-xs text-red-500 underline hover:text-red-700"
                  >
                    Try again
                  </button>
                </div>
              )}
            </>
          )}

          {/* Provider select */}
          <div className="mt-4">
            <label className="block text-xs font-medium text-slate-500 mb-1.5">
              AI Model
            </label>
            <select
              value={provider}
              onChange={(e) => onProviderChange(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
            >
              <option value="auto">Auto (Recommended)</option>
              <option value="gemini">Google Gemini</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-5 border-t border-slate-200">
        <button
          onClick={onGenerate}
          disabled={uiState === "generating"}
          className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary-hover disabled:opacity-60 text-white font-medium py-2.5 px-4 rounded-lg transition-colors"
        >
          <span className="material-symbols-outlined text-lg">
            auto_awesome
          </span>
          {uiState === "generating" ? "Generating..." : "Generate Diagram"}
        </button>
      </div>
    </div>
  );
}
