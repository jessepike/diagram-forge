"use client";

import { useEffect, useState } from "react";
import LeftPanel from "@/components/LeftPanel";
import RightPanel from "@/components/RightPanel";
import SettingsModal from "@/components/SettingsModal";

export interface Template {
  id: string;
  name: string;
  description: string;
  recommended_provider: string | null;
}

export type UIState = "initial" | "generating" | "success" | "error";
export type InputTab = "paste" | "upload";

export default function Home() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [contentInput, setContentInput] = useState("");
  const [inputTab, setInputTab] = useState<InputTab>("paste");
  const [provider, setProvider] = useState("auto");
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [generatedMeta, setGeneratedMeta] = useState<{
    provider: string;
    model: string;
    cost_usd: number;
  } | null>(null);
  const [uiState, setUiState] = useState<UIState>("initial");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settingsProvider, setSettingsProvider] = useState("auto");
  const [apiKey, setApiKey] = useState("");

  // Load settings from sessionStorage on mount
  useEffect(() => {
    const storedKey = sessionStorage.getItem("df_api_key");
    const storedProvider = sessionStorage.getItem("df_provider");
    if (storedKey) setApiKey(storedKey);
    if (storedProvider) {
      setSettingsProvider(storedProvider);
      setProvider(storedProvider);
    }
  }, []);

  // Fetch templates on mount
  useEffect(() => {
    fetch("/api/templates")
      .then((res) => res.json())
      .then((data: Template[]) => {
        setTemplates(data);
        if (data.length > 0) setSelectedTemplate(data[0].id);
      })
      .catch((err) => console.error("Failed to load templates:", err));
  }, []);

  const handleGenerate = async () => {
    if (!selectedTemplate || !contentInput.trim()) return;

    const resolvedProvider =
      provider === "auto" ? "gemini" : provider;

    setUiState("generating");
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          template_id: selectedTemplate,
          content: contentInput,
          provider: resolvedProvider,
          api_key: apiKey,
        }),
      });

      if (!res.ok) throw new Error(`Generation failed: ${res.status}`);

      const data = await res.json();
      setGeneratedImage(data.image_base64);
      setGeneratedMeta({
        provider: data.provider,
        model: data.model,
        cost_usd: data.cost_usd,
      });
      setUiState("success");
    } catch (err) {
      console.error("Generation error:", err);
      setUiState("error");
    }
  };

  const handleSaveSettings = (newProvider: string, newApiKey: string) => {
    setSettingsProvider(newProvider);
    setProvider(newProvider);
    setApiKey(newApiKey);
    sessionStorage.setItem("df_provider", newProvider);
    sessionStorage.setItem("df_api_key", newApiKey);
    setSettingsOpen(false);
  };

  return (
    <div className="flex h-screen">
      <LeftPanel
        templates={templates}
        selectedTemplate={selectedTemplate}
        onSelectTemplate={setSelectedTemplate}
        contentInput={contentInput}
        onContentChange={setContentInput}
        inputTab={inputTab}
        onTabChange={setInputTab}
        provider={provider}
        onProviderChange={setProvider}
        onGenerate={handleGenerate}
        onOpenSettings={() => setSettingsOpen(true)}
        uiState={uiState}
      />
      <RightPanel
        uiState={uiState}
        generatedImage={generatedImage}
        generatedMeta={generatedMeta}
        onRegenerate={handleGenerate}
      />
      {settingsOpen && (
        <SettingsModal
          provider={settingsProvider}
          apiKey={apiKey}
          onSave={handleSaveSettings}
          onClose={() => setSettingsOpen(false)}
        />
      )}
    </div>
  );
}
