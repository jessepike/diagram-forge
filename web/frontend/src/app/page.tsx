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
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [templatesLoading, setTemplatesLoading] = useState(true);
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
    setTemplatesLoading(true);
    fetch("/api/templates")
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          console.error("Template fetch error:", data.error);
          setTemplates([]);
        } else {
          const list = data as Template[];
          setTemplates(list);
          if (list.length > 0) setSelectedTemplate(list[0].id);
        }
      })
      .catch((err) => console.error("Failed to load templates:", err))
      .finally(() => setTemplatesLoading(false));
  }, []);

  const handleGenerate = async () => {
    if (!selectedTemplate) {
      setErrorMessage("Please select a template first.");
      setUiState("error");
      return;
    }
    if (!contentInput.trim()) {
      setErrorMessage("Please enter some content to generate a diagram from.");
      setUiState("error");
      return;
    }

    const resolvedProvider =
      provider === "auto"
        ? (templates.find((t) => t.id === selectedTemplate)?.recommended_provider || "gemini")
        : provider;

    setErrorMessage(null);
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

      const data = await res.json();

      if (!res.ok) {
        setErrorMessage(data.error || `Generation failed (${res.status})`);
        setUiState("error");
        return;
      }

      setGeneratedImage(data.image_base64);
      setGeneratedMeta({
        provider: data.provider,
        model: data.model,
        cost_usd: data.cost_usd,
      });
      setUiState("success");
    } catch {
      setErrorMessage("Network error — could not reach the server.");
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
        templatesLoading={templatesLoading}
      />
      <RightPanel
        uiState={uiState}
        generatedImage={generatedImage}
        generatedMeta={generatedMeta}
        onRegenerate={handleGenerate}
        errorMessage={errorMessage}
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
