import { useState } from "react";
import { ChevronDown, User, Shield, Wrench } from "lucide-react";
import { setRole } from "../api/client";

const roles = [
  { id: "field_engineer", label: "Field Engineer", icon: Wrench },
  { id: "maintenance_manager", label: "Maintenance Manager", icon: User },
  { id: "administrator", label: "Administrator", icon: Shield },
];

export default function RoleSwitcher() {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState(roles[0]);

  const handleSelect = (role) => {
    setSelected(role);
    setRole(role.id);
    setOpen(false);
    window.location.reload();
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg bg-[#241f1c] border border-[#332b26] text-sm text-[#e8e3dc] hover:border-[#d97706]/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          <selected.icon size={15} className="text-[#f59e0b]" />
          <span className="truncate">{selected.label}</span>
        </div>
        <ChevronDown size={14} className="text-[#a89a8c]" />
      </button>

      {open && (
        <div className="absolute bottom-full mb-1 w-full bg-[#1a1614] border border-[#332b26] rounded-lg overflow-hidden shadow-xl">
          {roles.map((role) => (
            <button
              key={role.id}
              onClick={() => handleSelect(role)}
              className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-left hover:bg-[#241f1c] text-[#a89a8c] hover:text-[#e8e3dc] transition-colors"
            >
              <role.icon size={15} />
              {role.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
