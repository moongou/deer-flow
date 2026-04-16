import re

with open("frontend/src/components/workspace/settings/model-settings-page.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Provide an updated OllamaTab
# We will use Regex or simply define a new function and replace it.
# First, we need to pass `providers` and `setConfiguring` to OllamaTab.
old_ollamatab_usage = """          <OllamaTab
            activeProvider={active.active_provider}
            activeModel={active.active_model}
            onSetActive={async (p, m) => { await setActiveModel(p, m); void refetchActive(); }}
          />"""

new_ollamatab_usage = """          <OllamaTab
            activeProvider={active.active_provider}
            activeModel={active.active_model}
            onSetActive={async (p, m) => { await setActiveModel(p, m); void refetchActive(); }}
            remoteOllama={providers.find((p) => p.id === "ollama-remote")}
            setConfiguring={setConfiguring}
          />"""

content = content.replace(old_ollamatab_usage, new_ollamatab_usage)


old_ollamatab_def = """function OllamaTab({
  activeProvider,
  activeModel,
  onSetActive,
}: {
  activeProvider: string | null;
  activeModel: string | null;
  onSetActive: (provider: string, model: string) => void;
}) {"""

new_ollamatab_def = """function OllamaTab({
  activeProvider,
  activeModel,
  onSetActive,
  remoteOllama,
  setConfiguring,
}: {
  activeProvider: string | null;
  activeModel: string | null;
  onSetActive: (provider: string, model: string) => void;
  remoteOllama?: ProviderInfo;
  setConfiguring: (p: ProviderInfo) => void;
}) {"""

content = content.replace(old_ollamatab_def, new_ollamatab_def)

# Replace the body of OllamaTab to have two columns
# original:
#   return (
#     <div className="space-y-4">
#       <div className="flex items-center justify-between"> ... </div>
#       ... scrollarea
#     </div>
#   );
import re
match = re.search(r"return \(\n    <div className=\"space-y-4\">[\s\S]*?Ollama 未运行[\s\S]*?</ScrollArea>\n          \)}[\s\S]*?</div>\n  \);", content)
if match:
    old_ollamatab_return = match.group(0)
    new_ollamatab_return = """return (
    <div className="grid grid-cols-2 gap-6 h-full items-start">
      {/* ---------- 左侧：本地 Ollama ---------- */}
      <div className="space-y-4 pr-2 border-r h-full">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🦙</span>
            <div>
              <p className="font-medium text-sm">Ollama 本地服务器</p>
              <p className="text-xs text-muted-foreground">端口: 11434 (无需 API Key)</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={running ? "default" : "secondary"} className={running ? "bg-green-600 font-normal" : "font-normal"}>
              {running ? "运行中" : "已停止"}
            </Badge>
            <Button variant="outline" size="sm" onClick={refresh} disabled={isLoading}>
              <RefreshCwIcon className={`size-3 ${isLoading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>

        <Separator />

        {error && (
          <p className="text-xs text-destructive bg-destructive/10 rounded p-2">
            无法连接: {error.message}
          </p>
        )}

        {!running && !error && (
          <div className="text-center py-6 text-muted-foreground border rounded bg-accent/20">
            <p className="text-sm">Ollama 未运行</p>
            <p className="text-xs mt-1">请先启动: <code className="bg-muted px-1 rounded">ollama serve</code></p>
          </div>
        )}

        {models.length > 0 && (
          <ScrollArea className="h-[380px] pr-3">
            <div className="space-y-2">
              {models.map((m) => {
                const isActive = activeProvider === "ollama" && activeModel === m.name;
                return (
                  <div
                    key={m.name}
                    className={`flex items-center justify-between rounded-md border p-2 cursor-pointer transition-colors hover:bg-accent/50 ${isActive ? "border-primary bg-primary/5" : ""}`}
                    onClick={() => {
                      if (!isActive) onSetActive("ollama", m.name);
                    }}
                  >
                    <div className="min-w-0">
                      <p className="font-mono text-sm font-medium truncate">{m.name}</p>
                      <div className="flex gap-2 mt-1">
                        {m.parameter_size && <span className="text-[10px] bg-muted px-1 rounded">{m.parameter_size}</span>}
                        {m.quantization && <span className="text-[10px] bg-muted px-1 rounded">{m.quantization}</span>}
                        {m.size_gb > 0 && <span className="text-[10px] bg-muted px-1 rounded">{m.size_gb}GB</span>}
                      </div>
                    </div>
                    {isActive ? (
                      <Button variant="default" size="sm" className="h-6 text-xs bg-primary text-primary-foreground pointer-events-none ml-2 shrink-0">
                        <CheckIcon className="size-3 mr-1" /> 已激活
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm" className="h-6 text-xs ml-2 shrink-0" onClick={(e) => { e.stopPropagation(); onSetActive("ollama", m.name); }}>
                        使用
                      </Button>
                    )}
                  </div>
                );
              })}
            </div>
          </ScrollArea>
        )}
      </div>

      {/* ---------- 右侧：远程 Ollama ---------- */}
      <div className="space-y-4 pl-2 h-full">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">☁️</span>
            <div>
              <p className="font-medium text-sm">Ollama 云端/远程</p>
              <p className="text-xs text-muted-foreground">需配置 Host / API Key</p>
            </div>
          </div>
          {remoteOllama && (
            <Button variant="default" size="sm" onClick={() => setConfiguring(remoteOllama)}>
              配置云端
            </Button>
          )}
        </div>

        <Separator />

        {remoteOllama ? (
          remoteOllama.has_key && remoteOllama.extra_models && remoteOllama.extra_models.length > 0 ? (
            <ScrollArea className="h-[380px] pr-3">
              <div className="space-y-2">
                {remoteOllama.extra_models.map((mName) => {
                  const isActive = activeProvider === remoteOllama.id && activeModel === mName;
                  return (
                    <div
                      key={mName}
                      className={`flex items-center justify-between rounded-md border p-2 cursor-pointer transition-colors hover:bg-accent/50 ${isActive ? "border-primary bg-primary/5" : ""}`}
                      onClick={() => {
                        if (!isActive) onSetActive(remoteOllama.id, mName);
                      }}
                    >
                      <p className="font-mono text-sm font-medium truncate">{mName}</p>
                      {isActive ? (
                        <Button variant="default" size="sm" className="h-6 text-xs bg-primary pointer-events-none ml-2 shrink-0">
                          <CheckIcon className="size-3 mr-1" /> 已激活
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm" className="h-6 text-xs ml-2 shrink-0" onClick={(e) => { e.stopPropagation(); onSetActive(remoteOllama.id, mName); }}>
                          使用
                        </Button>
                      )}
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          ) : (
            <div className="text-center py-6 border rounded bg-accent/20">
              <p className="text-sm text-muted-foreground mb-2">云端 Ollama 尚未配置或没有发现模型</p>
              <Button variant="outline" size="sm" onClick={() => setConfiguring(remoteOllama)}>
                立即配置并在测试时加载模型
              </Button>
            </div>
          )
        ) : (
          <div className="text-center py-6 text-muted-foreground text-sm">未找到远程 Ollama 提供商</div>
        )}
      </div>
    </div>
  );"""
    content = content.replace(old_ollamatab_return, new_ollamatab_return)
else:
    print("Could not find OllamaTab return body!")


# 2. Fix LocalServicesTab flashing issue
# We find where it returns <div className="flex items-center justify-center p-8 text-muted-foreground border rounded-lg bg-accent/20">
content = content.replace(
    "{services.length === 0 && !isLoading && !error && (",
    "{services.length === 0 && !isLoading && !error && ("
)

old_local_services = """function LocalServicesTab() {
  const { services, isLoading, error, refetch, toggleService } = useLocalServices();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-medium text-sm">localhost:9999 服务</p>
          <p className="text-xs text-muted-foreground">TTS/ASR/MinerU/Dify/Onyx 等</p>
        </div>
        <Button variant="outline" size="sm" onClick={refetch} disabled={isLoading}>
          <RefreshCwIcon className={`size-4 ${isLoading ? "animate-spin" : ""}`} />
          <span className="ml-1">刷新</span>
        </Button>
      </div>

      <Separator />

      {error && (
        <p className="text-sm text-destructive bg-destructive/10 rounded p-3">
          无法连接到 localhost:9999 服务管理器
        </p>
      )}

      {services.length === 0 && !isLoading && !error && (
        <div className="text-center py-8 text-muted-foreground">
          <ServerIcon className="size-8 mx-auto mb-2 opacity-40" />
          <p className="text-sm">没有发现本地服务</p>
        </div>
      )}"""

new_local_services = """function LocalServicesTab() {
  const { services, isLoading, error, refetch, toggleService } = useLocalServices();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-medium text-sm">本地服务集成</p>
          <p className="text-xs text-muted-foreground">本地运行的 TTS/ASR/MinerU/Onyx (通过 9999 端口) 提供支持</p>
        </div>
        <Button variant="outline" size="sm" onClick={refetch} disabled={isLoading}>
          <RefreshCwIcon className={`size-4 ${isLoading ? "animate-spin" : ""}`} />
          <span className="ml-1">{isLoading && services.length === 0 ? "加载中..." : "刷新"}</span>
        </Button>
      </div>

      <Separator />

      {error && (
        <p className="text-sm text-destructive bg-destructive/10 rounded p-3">
          无法连接到 localhost:9999。该服务未处于活跃状态。(如果你不需要外部服务则无需理会)
        </p>
      )}

      {services.length === 0 && !isLoading && !error && (
        <div className="text-center py-8 text-muted-foreground">
          <ServerIcon className="size-8 mx-auto mb-2 opacity-40" />
          <p className="text-sm">没有发现运行在 9999 的本地服务</p>
        </div>
      )}

      {services.length === 0 && isLoading && !error && (
        <div className="text-center py-8 text-muted-foreground">
          <RefreshCwIcon className="size-6 animate-spin mx-auto mb-2" />
          <p className="text-sm">正在加载中...</p>
        </div>
      )}"""

content = content.replace(old_local_services, new_local_services)


# 3. Redesign Current Config "Status" Tab to look tight and show active resources
# Find function StatusTab

old_status_tab = """function StatusTab({
  activeProvider,
  activeModel,
  providers,
}: {
  activeProvider: string | null;
  activeModel: string | null;
  providers: ProviderInfo[];
}) {
  const active = providers.find((p) => p.id === activeProvider);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-medium text-sm">当前生效模型</p>
          <p className="text-xs text-muted-foreground">全局生效的主力推断模型</p>
        </div>
      </div>
      <Separator />

      <Card className="border-primary/50 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-primary" />
        <CardContent className="p-6 flex flex-col items-center justify-center space-y-4">
          <div className="flex items-center justify-center p-4 bg-primary/10 rounded-full">
            <ZapIcon className="size-8 text-primary" />
          </div>
          {active ? (
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold flex items-center justify-center gap-2">
                <span>{active.icon}</span> {active.name}
              </h2>
              <p className="text-lg text-muted-foreground font-mono bg-muted px-3 py-1 rounded inline-block">
                {activeModel}
              </p>
            </div>
          ) : (
            <div className="text-center text-muted-foreground">
              <p className="mb-2">暂未配置主力模型</p>
              <p className="text-sm">请在 LLM 提供商选项卡中进行配置并点击激活</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}"""

new_status_tab = """function StatusTab({
  activeProvider,
  activeModel,
  providers,
}: {
  activeProvider: string | null;
  activeModel: string | null;
  providers: ProviderInfo[];
}) {
  const active = providers.find((p) => p.id === activeProvider);
  const enabledProviders = providers.filter((p) => p.enabled || p.has_key);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between border-b pb-2">
        <p className="font-medium text-sm flex items-center gap-2"><ZapIcon className="size-4 text-amber-500" /> 当前激活系统</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Active Model */}
        <Card className="border-primary/40 shadow-sm relative overflow-hidden">
          <div className="absolute top-0 left-0 w-[3px] h-full bg-primary" />
          <CardHeader className="py-2 px-4 bg-primary/5 border-b border-primary/10">
            <p className="text-xs font-semibold text-primary">全局默认模型</p>
          </CardHeader>
          <CardContent className="p-4 flex items-center gap-3">
            {active ? (
               <>
                 <span className="text-3xl">{active.icon}</span>
                 <div className="min-w-0">
                   <p className="font-bold text-sm truncate">{active.name}</p>
                   <p className="text-xs font-mono text-muted-foreground truncate">{activeModel}</p>
                 </div>
               </>
            ) : (
               <p className="text-xs text-muted-foreground py-2">未激活任何模型</p>
            )}
          </CardContent>
        </Card>

        {/* Enabled Configs Summary */}
        <Card className="shadow-sm">
          <CardHeader className="py-2 px-4 bg-muted/50 border-b">
            <p className="text-xs font-semibold text-muted-foreground">已配参数的 API</p>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-20">
              {enabledProviders.length > 0 ? (
                <div className="divide-y text-xs">
                  {enabledProviders.map(p => (
                    <div key={p.id} className="flex justify-between items-center p-2 px-4 hover:bg-muted/50">
                      <span className="flex items-center gap-1"><span className="text-base">{p.icon}</span> {p.name}</span>
                      <span className="text-[10px] text-muted-foreground">{p.has_key ? '已配密钥' : '无需密钥'}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-muted-foreground p-4 text-center">暂未配置任何提供商 API</p>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}"""

content = content.replace(old_status_tab, new_status_tab)


with open("frontend/src/components/workspace/settings/model-settings-page.tsx", "w", encoding="utf-8") as f:
    f.write(content)

