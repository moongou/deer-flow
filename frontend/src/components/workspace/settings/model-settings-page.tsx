"use client";

import {
  CheckIcon,
  KeyIcon,
  RefreshCwIcon,
  TrashIcon,
  ZapIcon,
} from "lucide-react";
import { useCallback, useState, type ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useActiveModel,
  useLocalServices,
  useOllamaModels,
  useProviders,
  useRemoveProviderAPIKey,
  useSetProviderAPIKey,
  useTestConnection,
  type ProviderInfo,
} from "@/core/user-models/hooks";
import { cn } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Provider configuration dialog
// ---------------------------------------------------------------------------

interface ProviderDialogProps {
  provider: ProviderInfo | null;
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
}

function ProviderDialog({ provider, open, onClose, onSaved }: ProviderDialogProps) {
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; models?: string[]; error?: string } | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>("");

  const { setAPIKey, isLoading: saving } = useSetProviderAPIKey();
  const { removeAPIKey, isLoading: removing } = useRemoveProviderAPIKey();
  const { testConnection } = useTestConnection();
  const { setActiveModel } = useActiveModel();

  const handleOpen = useCallback(() => {
    setApiKey("");
    setBaseUrl(provider?.base_url ?? "");
    setShowKey(false);
    setTestResult(null);
    setSelectedModel(provider?.active_model ?? "");
  }, [provider]);

  const handleTest = async () => {
    if (!provider) return;
    setTesting(true);
    setTestResult(null);
    try {
      const result = await testConnection(provider.id, apiKey || undefined, baseUrl || undefined);
      setTestResult(result);
    } catch (e) {
      setTestResult({ ok: false, error: String(e) });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!provider || !apiKey.trim()) return;
    await setAPIKey(provider.id, apiKey.trim(), baseUrl.trim() || undefined);
    onSaved();
    onClose();
  };

  const handleRemove = async () => {
    if (!provider) return;
    await removeAPIKey(provider.id);
    onSaved();
    onClose();
  };

  const handleActivate = async () => {
    if (!provider || !selectedModel) return;
    await setActiveModel(provider.id, selectedModel);
    onSaved();
    onClose();
  };

  const allModels = [
    ...(provider?.active_model ? [provider.active_model] : []),
    ...(provider?.default_models ?? []),
    ...(provider?.extra_models ?? []),
    ...(testResult?.models ?? []),
  ].filter((m, i, arr) => arr.indexOf(m) === i);

  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) onClose(); else handleOpen(); }}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <span className="text-2xl">{provider?.icon}</span>
            <span>{provider?.name}</span>
            {provider?.has_key && (
              <Badge variant="default" className="ml-2 bg-green-600 text-white">已配置</Badge>
            )}
          </DialogTitle>
          <DialogDescription className="text-sm">
            {provider?.description}
            <span className="mt-2 block text-xs leading-5 text-muted-foreground">
              “激活”只会把模型加入前端模型选择器，不会自动切换当前对话正在使用的模型。
            </span>
            {provider?.docs_url && (
              <a
                href={provider.docs_url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-blue-500 hover:underline text-xs"
              >
                文档 ↗
              </a>
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 pt-2">
          {/* API Key */}
          {provider?.group !== "local" && (
            <div className="space-y-1.5">
              <label className="text-sm font-medium">API Key</label>
              <div className="flex gap-2">
                <Input
                  type={showKey ? "text" : "password"}
                  placeholder={provider?.has_key ? "已设置 (输入新值覆盖)" : "sk-..."}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="flex-1 font-mono text-sm"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowKey(!showKey)}
                  className="shrink-0"
                >
                  <KeyIcon className="size-4" />
                </Button>
              </div>
            </div>
          )}

          {/* Base URL */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium">
              Base URL <span className="text-xs text-muted-foreground">(可选，留空使用默认值)</span>
            </label>
            <Input
              type="text"
              placeholder={provider?.base_url}
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              className="font-mono text-sm"
            />
          </div>

          {/* Test connection */}
          <div className="space-y-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleTest}
              disabled={testing || (!apiKey && !provider?.has_key && provider?.group !== "local")}
              className="w-full"
            >
              {testing ? (
                <RefreshCwIcon className="mr-2 size-4 animate-spin" />
              ) : (
                <ZapIcon className="mr-2 size-4" />
              )}
              {testing ? "正在测试..." : "测试连接 & 获取模型列表"}
            </Button>

            {testResult && (
              <div className={`rounded-md p-3 text-sm ${testResult.ok ? "bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800" : "bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800"}`}>
                {testResult.ok ? (
                  <>
                    <p className="font-medium text-green-700 dark:text-green-400 flex items-center gap-1">
                      <CheckIcon className="size-4" /> 连接成功！获取到 {testResult.models?.length ?? 0} 个模型
                    </p>
                  </>
                ) : (
                  <p className="text-red-700 dark:text-red-400">❌ {testResult.error}</p>
                )}
              </div>
            )}
          </div>

          {/* Model selector */}
          {allModels.length > 0 && (
            <div className="space-y-1.5">
              <label className="text-sm font-medium">选择要加入前端可选列表的模型</label>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger>
                  <SelectValue placeholder="选择模型..." />
                </SelectTrigger>
                <SelectContent>
                  {allModels.map((m) => (
                    <SelectItem key={m} value={m}>
                      <span className="font-mono text-xs">{m}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div>
            {provider?.has_key && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRemove}
                disabled={removing}
                className="text-destructive hover:text-destructive"
              >
                <TrashIcon className="mr-1 size-4" />
                移除 API Key
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose}>取消</Button>
            {selectedModel && (
              <Button onClick={handleActivate} className="bg-emerald-600 text-white hover:bg-emerald-500">
                <CheckIcon className="mr-1 size-4" />
                加入前端可选
              </Button>
            )}
            {(apiKey.trim() || provider?.group === "local") && (
              <Button onClick={handleSave} disabled={saving || (!apiKey.trim() && provider?.group !== "local")}>
                {saving ? "保存中..." : "保存"}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Provider card (ultra-compact single-line)
// ---------------------------------------------------------------------------

function ProviderCard({
  provider,
  active,
  onConfigure,
}: {
  provider: ProviderInfo;
  active: boolean;
  onConfigure: (p: ProviderInfo) => void;
}) {
  return (
    <button
      className={cn(
        "w-full flex items-center gap-2 rounded-xl px-3 py-2 text-left transition-all border",
        "bg-background/75 shadow-[0_1px_0_rgba(255,255,255,0.04)] hover:bg-accent/60",
        active
          ? "border-emerald-500/45 bg-emerald-500/10 text-emerald-700 ring-1 ring-emerald-500/20 dark:text-emerald-300"
          : "border-border/50 hover:border-border/80",
        !provider.enabled && "opacity-60",
      )}
      onClick={() => onConfigure(provider)}
    >
      <span className="text-sm leading-none shrink-0">{provider.icon}</span>
      <span
        className={cn(
          "text-xs font-medium truncate flex-1",
          active ? "text-emerald-700 dark:text-emerald-300" : "text-foreground",
        )}
      >
        {provider.name}
      </span>
      {provider.active_model && (
        <span className="text-[10px] font-mono text-muted-foreground truncate max-w-[84px] shrink-0">
          {provider.active_model.split("/").pop()}
        </span>
      )}
      {active ? (
        <Badge className="shrink-0 border-0 bg-emerald-600/90 px-1.5 py-0 text-[9px] text-white shadow-none">
          可选
        </Badge>
      ) : provider.has_key ? (
        <div className="size-1.5 rounded-full bg-green-500/80 shrink-0" />
      ) : provider.group === "local" ? (
        <div className="size-1.5 rounded-full bg-sky-400/70 shrink-0" />
      ) : (
        <div className="size-1.5 rounded-full bg-muted-foreground/25 shrink-0" />
      )}
    </button>
  );
}

function ActivatedBadge({ className, children = "前端可选" }: { className?: string; children?: ReactNode }) {
  return (
    <Badge className={cn("border-0 bg-emerald-600 text-white shadow-none", className)}>
      {children}
    </Badge>
  );
}

function SectionPanel({
  icon,
  title,
  subtitle,
  action,
  children,
}: {
  icon: string;
  title: string;
  subtitle: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="rounded-3xl border border-border/50 bg-[linear-gradient(180deg,rgba(255,255,255,0.78),rgba(248,250,252,0.94))] p-4 shadow-sm dark:bg-[linear-gradient(180deg,rgba(24,24,27,0.9),rgba(17,24,39,0.92))]">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div className="flex min-w-0 items-start gap-3">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-2xl border border-border/40 bg-background/80 text-xl shadow-sm">
            {icon}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold tracking-tight">{title}</p>
            <p className="mt-1 text-xs leading-5 text-muted-foreground">{subtitle}</p>
          </div>
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
      {children}
    </section>
  );
}

function SectionEmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-border/60 bg-muted/25 px-4 py-8 text-center">
      <p className="text-sm font-medium">{title}</p>
      <p className="mt-1 text-xs leading-5 text-muted-foreground">{description}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Ollama tab
// ---------------------------------------------------------------------------

function OllamaTab({
  localActivatedModel,
  remoteActivatedModel,
  onSetActive,
  remoteOllama,
  setConfiguring,
}: {
  localActivatedModel: string | null;
  remoteActivatedModel: string | null;
  onSetActive: (provider: string, model: string) => void;
  remoteOllama?: ProviderInfo;
  setConfiguring: (p: ProviderInfo) => void;
}) {
  const { models, running, isLoading, error, refresh } = useOllamaModels();
  const remoteModelNames = [
    ...(remoteOllama?.active_model ? [remoteOllama.active_model] : []),
    ...(remoteOllama?.extra_models ?? []),
  ].filter((name, index, arr) => arr.indexOf(name) === index);

  return (
    <div className="grid grid-cols-2 gap-4 h-full items-start">
      <SectionPanel
        icon="🦙"
        title="Ollama 本地节点"
        subtitle="把本地 Ollama 模型加入前端可选列表。这里只负责登记可选模型，不会切换当前会话。"
        action={
          <div className="flex items-center gap-2">
            <Badge variant={running ? "default" : "secondary"} className={running ? "bg-emerald-600 font-normal text-white" : "font-normal"}>
              {running ? "在线" : "离线"}
            </Badge>
            <Button variant="outline" size="sm" onClick={refresh} disabled={isLoading}>
              <RefreshCwIcon className={cn("size-3", isLoading && "animate-spin")} />
            </Button>
          </div>
        }
      >
        {error ? (
          <p className="rounded-2xl border border-destructive/20 bg-destructive/10 p-3 text-xs text-destructive">
            无法连接到本地 Ollama: {error.message}
          </p>
        ) : null}

        {!running && !error ? (
          <SectionEmptyState
            title="本地 Ollama 尚未启动"
            description="请先运行 ollama serve，启动后点击右上角刷新。"
          />
        ) : null}

        {models.length > 0 ? (
          <ScrollArea className="h-[420px] pr-1">
            <div className="space-y-2">
              {models.map((m) => {
                const isActivated = localActivatedModel === m.name;
                return (
                  <div
                    key={m.name}
                    className={cn(
                      "flex items-center justify-between gap-3 rounded-2xl border px-3 py-3 transition-all",
                      isActivated
                        ? "border-emerald-500/40 bg-emerald-500/10 shadow-sm"
                        : "border-border/50 bg-background/75 hover:border-border/80 hover:bg-accent/35",
                    )}
                  >
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <p className="truncate font-mono text-sm font-semibold">{m.name}</p>
                        {isActivated ? <ActivatedBadge className="px-2 py-0.5 text-[10px]" /> : null}
                      </div>
                      <div className="mt-2 flex flex-wrap gap-1.5 text-[10px] text-muted-foreground">
                        {m.parameter_size ? <span className="rounded-full bg-muted px-2 py-1">{m.parameter_size}</span> : null}
                        {m.quantization ? <span className="rounded-full bg-muted px-2 py-1">{m.quantization}</span> : null}
                        {m.size_gb > 0 ? <span className="rounded-full bg-muted px-2 py-1">{m.size_gb} GB</span> : null}
                      </div>
                    </div>
                    <Button
                      variant={isActivated ? "secondary" : "outline"}
                      size="sm"
                      className={cn(
                        "h-8 shrink-0 rounded-full px-3 text-xs",
                        isActivated && "border-0 bg-emerald-600 text-white hover:bg-emerald-600",
                      )}
                      onClick={() => {
                        if (!isActivated) {
                          onSetActive("ollama", m.name);
                        }
                      }}
                    >
                      {isActivated ? "前端可选" : "加入前端"}
                    </Button>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        ) : null}
      </SectionPanel>

      <SectionPanel
        icon="☁️"
        title="Ollama 远程集群"
        subtitle="远端节点需要先完成 Host/API 配置。激活后，该模型会稳定保存在前端可选列表中。"
        action={
          remoteOllama ? (
            <Button
              size="sm"
              className="rounded-full bg-slate-900 px-4 text-white hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white"
              onClick={() => setConfiguring(remoteOllama)}
            >
              {remoteOllama.has_key ? "修改配置" : "开始配置"}
            </Button>
          ) : null
        }
      >
        {!remoteOllama ? (
          <SectionEmptyState
            title="未发现远端 Ollama 提供商"
            description="请确认预设提供商是否已注册，或重新加载模型配置。"
          />
        ) : remoteOllama.has_key && remoteModelNames.length > 0 ? (
          <ScrollArea className="h-[420px] pr-1">
            <div className="space-y-2">
              {remoteModelNames.map((modelName) => {
                const isActivated = remoteActivatedModel === modelName;
                return (
                  <div
                    key={modelName}
                    className={cn(
                      "flex items-center justify-between gap-3 rounded-2xl border px-3 py-3 transition-all",
                      isActivated
                        ? "border-emerald-500/40 bg-emerald-500/10 shadow-sm"
                        : "border-border/50 bg-background/75 hover:border-border/80 hover:bg-accent/35",
                    )}
                  >
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <p className="truncate font-mono text-sm font-semibold">{modelName}</p>
                        {isActivated ? <ActivatedBadge className="px-2 py-0.5 text-[10px]" /> : null}
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">远端模型会同步进入聊天框中的模型选择器。</p>
                    </div>
                    <Button
                      variant={isActivated ? "secondary" : "outline"}
                      size="sm"
                      className={cn(
                        "h-8 shrink-0 rounded-full px-3 text-xs",
                        isActivated && "border-0 bg-emerald-600 text-white hover:bg-emerald-600",
                      )}
                      onClick={() => {
                        if (!isActivated) {
                          onSetActive(remoteOllama.id, modelName);
                        }
                      }}
                    >
                      {isActivated ? "前端可选" : "加入前端"}
                    </Button>
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        ) : (
          <SectionEmptyState
            title="远端模型尚未加载"
            description="先配置远端地址并测试连接；选中的模型会被保留并显示在前端模型列表中。"
            action={
              <Button variant="outline" size="sm" onClick={() => setConfiguring(remoteOllama)}>
                立即配置并加载
              </Button>
            }
          />
        )}
      </SectionPanel>
    </div>
  );
}
// ---------------------------------------------------------------------------

function LocalServicesTab() {
  const { services, isLoading, error, refetch, toggleService } = useLocalServices();

  return (
    <SectionPanel
      icon="🔧"
      title="本地服务集成"
      subtitle="统一管理接入 9999 端口的本地能力，例如 TTS、ASR、OCR 或知识检索服务。"
      action={
        <Button variant="outline" size="sm" onClick={refetch} disabled={isLoading}>
          <RefreshCwIcon className={cn("size-4", isLoading && "animate-spin")} />
          <span className="ml-1">{isLoading && services.length === 0 ? "加载中..." : "刷新"}</span>
        </Button>
      }
    >
      {error ? (
        <p className="rounded-2xl border border-destructive/20 bg-destructive/10 p-3 text-sm text-destructive">
          无法连接到 localhost:9999。如果你不依赖外部本地服务，可以忽略该提示。
        </p>
      ) : null}

      {services.length === 0 && !isLoading && !error ? (
        <SectionEmptyState
          title="没有发现可接入的本地服务"
          description="当 9999 端口暴露服务清单后，这里会显示每个能力模块的开关状态。"
        />
      ) : null}

      {services.length === 0 && isLoading && !error ? (
        <SectionEmptyState
          title="正在拉取本地服务状态"
          description="稍后会显示服务健康状态、端口以及前端开关。"
        />
      ) : null}

      <div className="space-y-2">
        {services.map((svc) => (
          <div
            key={svc.id}
            className="flex items-center justify-between gap-3 rounded-2xl border border-border/50 bg-background/75 px-3 py-3"
          >
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <p className="truncate text-sm font-semibold">{svc.name ?? svc.id}</p>
                <Badge
                  variant="outline"
                  className={cn(
                    "rounded-full px-2 py-0.5 text-[10px]",
                    svc.status === "running"
                      ? "border-emerald-500/50 text-emerald-700 dark:text-emerald-300"
                      : "text-muted-foreground",
                  )}
                >
                  {svc.status === "running" ? "运行中" : String(svc.status ?? "unknown")}
                </Badge>
              </div>
              {svc.description ? (
                <p className="mt-1 truncate text-xs text-muted-foreground">{String(svc.description)}</p>
              ) : null}
              {svc.port ? (
                <p className="mt-2 inline-flex rounded-full bg-muted px-2 py-1 font-mono text-[10px] text-muted-foreground">
                  :{String(svc.port)}
                </p>
              ) : null}
            </div>
            <div className="flex items-center gap-3">
              {svc.user_enabled ? <ActivatedBadge className="px-2 py-0.5 text-[10px]" /> : null}
              <Switch
                checked={svc.user_enabled}
                onCheckedChange={(v) => toggleService(String(svc.id), v)}
                className="shrink-0"
              />
            </div>
          </div>
        ))}
      </div>
    </SectionPanel>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function ModelSettingsPage() {
  const { providers, isLoading, refetch } = useProviders();
  const { active, setActiveModel, refetch: refetchActive } = useActiveModel();
  const [configuring, setConfiguring] = useState<ProviderInfo | null>(null);

  const localOllama = providers.find((provider) => provider.id === "ollama");
  const remoteOllama = providers.find((provider) => provider.id === "ollama-remote");
  const activatedProviders = providers.filter((provider) => provider.active_model);
  const configuredProviders = providers.filter((provider) => provider.has_key || provider.group === "local");

  const handleSaved = useCallback(() => {
    void refetch();
    void refetchActive();
  }, [refetch, refetchActive]);

  const handleActivateModel = useCallback(
    async (providerId: string, modelId: string) => {
      await setActiveModel(providerId, modelId);
      void refetch();
      void refetchActive();
    },
    [refetch, refetchActive, setActiveModel],
  );

  // "local" group is kept but Ollama entries have their own dedicated tab
  const groups = ["international", "china", "local", "custom"] as const;

  const byGroup = groups.reduce(
    (acc, g) => {
      acc[g] = providers.filter(
        (p) => p.group === g && p.id !== "ollama" && p.id !== "ollama-remote",
      );
      return acc;
    },
    {} as Record<(typeof groups)[number], ProviderInfo[]>,
  );

  return (
    <div className="h-full flex flex-col p-4 gap-0">
      <Tabs defaultValue="providers" className="flex-1 flex flex-col min-h-0">
        {/* ---- Modern tab header — fixed, never scrolls ---- */}
        <TabsList className="w-full shrink-0 grid grid-cols-4 mb-3 h-16 rounded-2xl bg-gradient-to-b from-muted/60 to-muted/30 border border-border/40 shadow-sm p-1.5 gap-1">
          <TabsTrigger
            value="providers"
            className="flex flex-col items-center justify-center gap-0.5 h-full rounded-xl text-[10px] font-semibold tracking-wide transition-all data-[state=active]:bg-background data-[state=active]:shadow-md data-[state=active]:text-primary data-[state=inactive]:text-muted-foreground/60"
          >
            <span className="text-lg leading-none">🤖</span>
            LLM 提供商
          </TabsTrigger>
          <TabsTrigger
            value="ollama"
            className="flex flex-col items-center justify-center gap-0.5 h-full rounded-xl text-[10px] font-semibold tracking-wide transition-all data-[state=active]:bg-background data-[state=active]:shadow-md data-[state=active]:text-primary data-[state=inactive]:text-muted-foreground/60"
          >
            <span className="text-lg leading-none">🦙</span>
            Ollama
          </TabsTrigger>
          <TabsTrigger
            value="services"
            className="flex flex-col items-center justify-center gap-0.5 h-full rounded-xl text-[10px] font-semibold tracking-wide transition-all data-[state=active]:bg-background data-[state=active]:shadow-md data-[state=active]:text-primary data-[state=inactive]:text-muted-foreground/60"
          >
            <span className="text-lg leading-none">🔧</span>
            本地服务
          </TabsTrigger>
          <TabsTrigger
            value="status"
            className="flex flex-col items-center justify-center gap-0.5 h-full rounded-xl text-[10px] font-semibold tracking-wide transition-all data-[state=active]:bg-background data-[state=active]:shadow-md data-[state=active]:text-primary data-[state=inactive]:text-muted-foreground/60"
          >
            <span className="text-lg leading-none">📌</span>
            状态总览
          </TabsTrigger>
        </TabsList>

        {/* ---- Providers tab ---- */}
        <TabsContent value="providers" className="flex-1 overflow-y-auto mt-1 data-[state=inactive]:hidden">
          {isLoading ? (
            <div className="flex items-center justify-center py-12 text-muted-foreground">
              <RefreshCwIcon className="size-5 animate-spin mr-2" />
              加载中...
            </div>
          ) : (
            <div className="space-y-3 pr-1 pb-2">
              {/* Two-column layout: international (left) | china (right) */}
              <div className="grid grid-cols-2 gap-4">
                {/* Left: International providers */}
                <SectionPanel icon="🌐" title="国际提供商" subtitle="适合 OpenAI、Anthropic、Gemini、OpenRouter 等国际模型源。">
                  <div className="flex items-center gap-1.5 mb-2 pb-1 border-b border-border/50">
                    <span className="text-sm">🌐</span>
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">国际提供商</span>
                  </div>
                  <div className="space-y-0.5">
                    {byGroup.international.map((p) => (
                      <ProviderCard
                        key={p.id}
                        provider={p}
                        active={Boolean(p.active_model)}
                        onConfigure={setConfiguring}
                      />
                    ))}
                  </div>
                </SectionPanel>
                {/* Right: China providers */}
                <SectionPanel icon="🇨🇳" title="国内提供商" subtitle="适合豆包、通义、智谱、月之暗面等国内模型源。">
                  <div className="flex items-center gap-1.5 mb-2 pb-1 border-b border-border/50">
                    <span className="text-sm">🇨🇳</span>
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">国内提供商</span>
                  </div>
                  <div className="space-y-0.5">
                    {byGroup.china.map((p) => (
                      <ProviderCard
                        key={p.id}
                        provider={p}
                        active={Boolean(p.active_model)}
                        onConfigure={setConfiguring}
                      />
                    ))}
                  </div>
                </SectionPanel>
              </div>

              {/* Bottom row: Local + Custom (shown only when present) */}
              {(byGroup.local.length > 0 || byGroup.custom.length > 0) && (
                <div className="grid grid-cols-2 gap-4 pt-1">
                  {byGroup.local.length > 0 && (
                    <SectionPanel icon="💻" title="本地模型入口" subtitle="LM Studio、llama.cpp 等本地 OpenAI 兼容服务。">
                      <div className="flex items-center gap-1.5 mb-2 pb-1 border-b border-border/50">
                        <span className="text-sm">💻</span>
                        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">本地模型</span>
                      </div>
                      <div className="space-y-0.5">
                        {byGroup.local.map((p) => (
                          <ProviderCard
                            key={p.id}
                            provider={p}
                            active={Boolean(p.active_model)}
                            onConfigure={setConfiguring}
                          />
                        ))}
                      </div>
                    </SectionPanel>
                  )}
                  {byGroup.custom.length > 0 && (
                    <SectionPanel icon="⚙️" title="自定义提供商" subtitle="适合企业网关、私有代理或其他 OpenAI 兼容端点。">
                      <div className="flex items-center gap-1.5 mb-2 pb-1 border-b border-border/50">
                        <span className="text-sm">⚙️</span>
                        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">自定义</span>
                      </div>
                      <div className="space-y-0.5">
                        {byGroup.custom.map((p) => (
                          <ProviderCard
                            key={p.id}
                            provider={p}
                            active={Boolean(p.active_model)}
                            onConfigure={setConfiguring}
                          />
                        ))}
                      </div>
                    </SectionPanel>
                  )}
                </div>
              )}
            </div>
          )}
        </TabsContent>

        {/* ---- Ollama tab ---- */}
        <TabsContent value="ollama" className="flex-1 overflow-y-auto mt-1 data-[state=inactive]:hidden">
          <OllamaTab
            localActivatedModel={localOllama?.active_model ?? (active.active_provider === "ollama" ? active.active_model : null)}
            remoteActivatedModel={remoteOllama?.active_model ?? (active.active_provider === "ollama-remote" ? active.active_model : null)}
            onSetActive={handleActivateModel}
            remoteOllama={remoteOllama}
            setConfiguring={setConfiguring}
          />
        </TabsContent>

        {/* ---- Local services tab ---- */}
        <TabsContent value="services" className="flex-1 overflow-y-auto mt-1 data-[state=inactive]:hidden">
          <LocalServicesTab />
        </TabsContent>

        {/* ---- Status tab ---- */}
        <TabsContent value="status" className="flex-1 overflow-y-auto mt-1 data-[state=inactive]:hidden">
          <div className="space-y-4">
            <SectionPanel
              icon="📌"
              title="最近加入前端的模型"
              subtitle="这里显示最近一次执行“加入前端可选”的模型，它会出现在聊天框模型选择器中，但不会替换当前会话模型。"
            >
              {active.active_model ? (
                <div className="flex items-center gap-3 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-4">
                  <span className="text-3xl">
                    {providers.find((provider) => provider.id === active.active_provider)?.icon ?? "🤖"}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-mono text-sm font-semibold">{active.active_model}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {providers.find((provider) => provider.id === active.active_provider)?.name ?? active.active_provider}
                    </p>
                  </div>
                  <ActivatedBadge />
                </div>
              ) : (
                <SectionEmptyState
                  title="还没有模型加入前端"
                  description="在任意提供商页点击“加入前端”后，模型会立刻出现在聊天输入框的模型选择器中。"
                />
              )}
            </SectionPanel>

            <SectionPanel
              icon="🧭"
              title="已加入前端的模型"
              subtitle="每个提供商最多保留一个前端可选模型。你可以把它理解为“登记到前端”，而不是“当前正在使用”。"
            >
              {activatedProviders.length === 0 ? (
                <SectionEmptyState
                  title="暂无前端可选模型"
                  description="当某个提供商的模型被加入前端后，会在这里形成一份清晰的可选清单。"
                />
              ) : (
                <div className="space-y-2">
                  {activatedProviders.map((provider) => (
                    <div
                      key={provider.id}
                      className="flex items-center gap-3 rounded-2xl border border-border/50 bg-background/75 px-3 py-3"
                    >
                      <span className="text-xl">{provider.icon}</span>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-semibold">{provider.name}</p>
                        <p className="mt-1 truncate font-mono text-xs text-muted-foreground">{provider.active_model}</p>
                      </div>
                      <ActivatedBadge className="px-2 py-0.5 text-[10px]" />
                    </div>
                  ))}
                </div>
              )}
            </SectionPanel>

            <SectionPanel
              icon="🗂️"
              title="已配置的提供商"
              subtitle="用于区分“已经接入”与“已加入前端可选”的关系，便于快速排查为什么某个模型暂时看不到。"
            >
              {configuredProviders.length === 0 ? (
                <SectionEmptyState
                  title="尚未配置任何提供商"
                  description="先为提供商填写 API Key 或启用本地服务，再把对应模型加入前端。"
                />
              ) : (
                <div className="space-y-2">
                  {configuredProviders.map((provider) => (
                    <div
                      key={provider.id}
                      className="flex items-center gap-3 rounded-2xl border border-border/50 bg-background/75 px-3 py-3"
                    >
                      <span className="text-xl">{provider.icon}</span>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-semibold">{provider.name}</p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          {provider.active_model ? "已接入，且已有前端可选模型" : "已接入，但尚未加入前端可选模型"}
                        </p>
                      </div>
                      {provider.active_model ? (
                        <ActivatedBadge className="px-2 py-0.5 text-[10px]" />
                      ) : provider.group === "local" ? (
                        <Badge variant="outline" className="rounded-full text-[10px]">本地</Badge>
                      ) : (
                        <Badge variant="secondary" className="rounded-full bg-slate-100 text-[10px] text-slate-700 dark:bg-slate-800 dark:text-slate-200">已配置</Badge>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </SectionPanel>
          </div>
        </TabsContent>
      </Tabs>

      {/* Provider configuration dialog */}
      <ProviderDialog
        provider={configuring}
        open={!!configuring}
        onClose={() => setConfiguring(null)}
        onSaved={handleSaved}
      />
    </div>
  );
}