import { useEffect, useState } from "react";
import { Activity, Shield, Server, Database } from "lucide-react";
import { api, getRole } from "../api/client";

export default function Monitoring() {
  const [health, setHealth] = useState(null);
  const [roles, setRoles] = useState(null);
  const [me, setMe] = useState(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => {});
    api.getRoles().then(setRoles).catch(() => {});
    api.getMe().then(setMe).catch(() => {});
  }, []);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <div className="text-xs font-bold tracking-widest text-[#f59e0b] uppercase mb-1">
          Admin Panel
        </div>
        <h1 className="text-3xl font-bold text-white">Monitoring</h1>
        <p className="text-[#a89a8c] text-sm mt-1">
          System health, RBAC configuration, and current session
        </p>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Server size={16} className="text-[#f59e0b]" />
            <span className="text-xs font-semibold text-[#f59e0b] uppercase tracking-wide">
              System Health
            </span>
          </div>
          {health ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#a89a8c]">Overall Status</span>
                <span className={`text-sm font-semibold ${health.status === "healthy" ? "text-[#10b981]" : "text-[#ef4444]"}`}>
                  {health.status}
                </span>
              </div>
              {health.services && Object.entries(health.services).map(([name, svc]) => (
                <div key={name} className="flex items-center justify-between">
                  <span className="text-sm text-[#a89a8c] capitalize">{name}</span>
                  <span className={`text-xs font-medium ${svc.status === "healthy" ? "text-[#10b981]" : "text-[#ef4444]"}`}>
                    {svc.status}
                  </span>
                </div>
              ))}
              <div className="flex items-center justify-between pt-3 border-t border-[#332b26]">
                <span className="text-sm text-[#a89a8c]">Latency</span>
                <span className="text-sm text-white">{Math.round(health.latency_ms)}ms</span>
              </div>
            </div>
          ) : (
            <div className="text-sm text-[#a89a8c]">Loading...</div>
          )}
        </div>

        <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Shield size={16} className="text-[#f59e0b]" />
            <span className="text-xs font-semibold text-[#f59e0b] uppercase tracking-wide">
              Current Session
            </span>
          </div>
          {me ? (
            <div className="space-y-3">
              <div>
                <div className="text-xs text-[#a89a8c] mb-1">User</div>
                <div className="text-sm text-white">{me.username}</div>
              </div>
              <div>
                <div className="text-xs text-[#a89a8c] mb-1">Role</div>
                <div className="text-sm text-white capitalize">{me.role?.replace(/_/g, " ")}</div>
              </div>
              <div>
                <div className="text-xs text-[#a89a8c] mb-2">Permissions</div>
                <div className="flex flex-wrap gap-1.5">
                  {me.permissions?.map((p, i) => (
                    <span key={i} className="text-xs bg-[#0a0908] border border-[#332b26] px-2 py-0.5 rounded text-[#a89a8c]">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-sm text-[#a89a8c]">Loading...</div>
          )}
        </div>
      </div>

      <div className="bg-[#1a1614] border border-[#332b26] rounded-xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <Database size={16} className="text-[#f59e0b]" />
          <span className="text-xs font-semibold text-[#f59e0b] uppercase tracking-wide">
            RBAC Configuration
          </span>
        </div>
        {roles ? (
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(roles).map(([roleName, roleData]) => (
              <div key={roleName} className="bg-[#0a0908] border border-[#332b26] rounded-lg p-4">
                <div className="text-sm font-semibold text-white capitalize mb-2">
                  {roleName.replace(/_/g, " ")}
                </div>
                <div className="text-xs text-[#a89a8c] mb-3">
                  {roleData.permission_count} permissions
                </div>
                <div className="space-y-1">
                  {roleData.permissions?.map((p, i) => (
                    <div key={i} className="text-xs text-[#a89a8c]">• {p}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-[#a89a8c]">Loading...</div>
        )}
      </div>
    </div>
  );
}
