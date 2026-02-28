interface TemplateCardProps {
  id: string;
  name: string;
  description: string;
  isActive: boolean;
  onClick: () => void;
}

const TEMPLATE_ICONS: Record<string, string> = {
  architecture: "account_tree",
  "system-context": "hub",
  "data-flow": "swap_horiz",
  "entity-relationship": "schema",
  "sequence-diagram": "timeline",
  "class-diagram": "class",
  "network-topology": "lan",
  "deployment-diagram": "cloud_upload",
  "state-machine": "radio_button_checked",
  "user-flow": "person_pin_circle",
  "api-architecture": "api",
  "microservices-map": "grid_view",
  infographic: "insert_chart",
};

export default function TemplateCard({
  id,
  name,
  description,
  isActive,
  onClick,
}: TemplateCardProps) {
  const icon = TEMPLATE_ICONS[id] ?? "category";

  return (
    <button
      onClick={onClick}
      className={`w-full text-left flex items-start gap-3 p-3 rounded-lg border transition-colors ${
        isActive
          ? "bg-slate-100 border-transparent"
          : "border-transparent hover:bg-slate-50 hover:border-slate-200"
      }`}
    >
      <span className="material-symbols-outlined text-slate-500 text-xl mt-0.5">
        {icon}
      </span>
      <div className="min-w-0">
        <div className="text-sm font-medium text-slate-900">{name}</div>
        <div className="text-xs text-slate-500 truncate">{description}</div>
      </div>
    </button>
  );
}
