import type { UIState } from "@/app/page";

interface RightPanelProps {
  uiState: UIState;
  generatedImage: string | null;
  generatedMeta: {
    provider: string;
    model: string;
    cost_usd: number;
  } | null;
  onRegenerate: () => void;
}

const EXAMPLE_PROMPTS = [
  "Microservices with API Gateway",
  "CI/CD Pipeline Architecture",
  "Event-Driven System Design",
];

export default function RightPanel({
  uiState,
  generatedImage,
  generatedMeta,
  onRegenerate,
}: RightPanelProps) {
  const handleDownload = () => {
    if (!generatedImage) return;
    const link = document.createElement("a");
    link.href = `data:image/png;base64,${generatedImage}`;
    link.download = "diagram.png";
    link.click();
  };

  return (
    <div className="flex-1 relative dot-grid overflow-hidden">
      {/* Floating toolbar */}
      <div className="absolute top-4 right-4 flex items-center gap-1 z-10">
        <button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-white/80 rounded-lg transition-colors">
          <span className="material-symbols-outlined text-xl">download</span>
        </button>
        <button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-white/80 rounded-lg transition-colors">
          <span className="material-symbols-outlined text-xl">share</span>
        </button>
        <button className="p-2 text-slate-400 hover:text-slate-600 hover:bg-white/80 rounded-lg transition-colors">
          <span className="material-symbols-outlined text-xl">fullscreen</span>
        </button>
      </div>

      {uiState === "initial" || uiState === "error" ? (
        /* Empty / Initial state */
        <div className="flex flex-col items-center justify-center h-full text-center px-8">
          {/* Spinning dashed circle */}
          <div className="w-20 h-20 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center mb-6 animate-spin [animation-duration:12s]">
            <span className="material-symbols-outlined text-3xl text-slate-300 animate-spin [animation-duration:12s] [animation-direction:reverse]">
              auto_awesome
            </span>
          </div>
          <h2 className="text-xl font-semibold text-slate-700 mb-2">
            Ready to Forge
          </h2>
          <p className="text-sm text-slate-500 max-w-sm mb-6">
            Select a template, paste your content, and click Generate to create
            a professional architecture diagram.
          </p>
          {uiState === "error" && (
            <p className="text-sm text-red-500 mb-4">
              Generation failed. Please check your API key and try again.
            </p>
          )}
          <div className="flex flex-wrap gap-2 justify-center">
            {EXAMPLE_PROMPTS.map((prompt) => (
              <span
                key={prompt}
                className="px-3 py-1.5 text-xs text-slate-500 bg-white rounded-full border border-slate-200"
              >
                {prompt}
              </span>
            ))}
          </div>
        </div>
      ) : uiState === "generating" ? (
        /* Generating state */
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="w-20 h-20 rounded-full border-2 border-dashed border-primary flex items-center justify-center mb-6 animate-spin [animation-duration:3s]">
            <span className="material-symbols-outlined text-3xl text-primary animate-spin [animation-duration:3s] [animation-direction:reverse]">
              auto_awesome
            </span>
          </div>
          <h2 className="text-xl font-semibold text-slate-700 mb-2">
            Generating Diagram...
          </h2>
          <p className="text-sm text-slate-500">
            This usually takes 10-30 seconds
          </p>
        </div>
      ) : (
        /* Success state */
        <div className="flex flex-col items-center justify-center h-full p-8">
          {/* Image container with macOS toolbar */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden max-w-4xl w-full">
            {/* macOS toolbar */}
            <div className="flex items-center justify-between px-4 py-2.5 bg-slate-50 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-yellow-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
              </div>
              <div className="flex items-center gap-1">
                <button className="p-1 text-slate-400 hover:text-slate-600">
                  <span className="material-symbols-outlined text-base">
                    zoom_out
                  </span>
                </button>
                <span className="text-xs text-slate-400 px-2">100%</span>
                <button className="p-1 text-slate-400 hover:text-slate-600">
                  <span className="material-symbols-outlined text-base">
                    zoom_in
                  </span>
                </button>
              </div>
            </div>
            {/* Image */}
            <div className="aspect-[16/9] bg-slate-50 flex items-center justify-center">
              {generatedImage && (
                <img
                  src={`data:image/png;base64,${generatedImage}`}
                  alt="Generated diagram"
                  className="w-full h-full object-contain"
                />
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3 mt-6">
            <button
              onClick={onRegenerate}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <span className="material-symbols-outlined text-base">
                refresh
              </span>
              Regenerate
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary-hover rounded-lg transition-colors"
            >
              <span className="material-symbols-outlined text-base">
                download
              </span>
              Download PNG
            </button>
          </div>

          {/* Meta + disclaimer */}
          {generatedMeta && (
            <p className="text-xs text-slate-400 mt-4">
              Generated with {generatedMeta.provider} ({generatedMeta.model}) —
              ${generatedMeta.cost_usd.toFixed(4)}
            </p>
          )}
          <p className="text-xs text-slate-400 mt-1">
            AI-generated diagram. Review for accuracy before use.
          </p>
        </div>
      )}
    </div>
  );
}
