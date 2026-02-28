"use client";

import { useState } from "react";

interface SettingsModalProps {
  provider: string;
  apiKey: string;
  onSave: (provider: string, apiKey: string) => void;
  onClose: () => void;
}

export default function SettingsModal({
  provider,
  apiKey,
  onSave,
  onClose,
}: SettingsModalProps) {
  const [localProvider, setLocalProvider] = useState(provider);
  const [localKey, setLocalKey] = useState(apiKey);
  const [showKey, setShowKey] = useState(false);

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative z-50 w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-xl text-slate-600">
              settings
            </span>
            <h2 className="text-lg font-semibold text-slate-900">Settings</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <span className="material-symbols-outlined text-xl">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-5">
          {/* Provider */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              AI Provider
            </label>
            <select
              value={localProvider}
              onChange={(e) => setLocalProvider(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
            >
              <option value="auto">Auto (Recommended)</option>
              <option value="gemini">Google Gemini</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>

          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              API Key
            </label>
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                value={localKey}
                onChange={(e) => setLocalKey(e.target.value)}
                placeholder="Enter your API key"
                className="w-full px-3 py-2 pr-10 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600"
              >
                <span className="material-symbols-outlined text-lg">
                  {showKey ? "visibility_off" : "visibility"}
                </span>
              </button>
            </div>
            <div className="mt-2 flex gap-3 text-xs">
              <a
                href="https://aistudio.google.com/apikey"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Get a Gemini key
              </a>
              <a
                href="https://platform.openai.com/api-keys"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Get an OpenAI key
              </a>
            </div>
          </div>

          {/* Security info */}
          <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
            <span className="material-symbols-outlined text-blue-600 text-lg mt-0.5">
              shield_lock
            </span>
            <p className="text-xs text-blue-700">
              Your API key is stored in your browser session only and is never
              saved to disk. It will be cleared when you close this tab.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-100">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(localProvider, localKey)}
            className="px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary-hover rounded-lg transition-colors active:scale-95"
          >
            Save for this session
          </button>
        </div>
      </div>
    </div>
  );
}
