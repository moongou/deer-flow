with open("/Users/m3max/VS-CODE-PROJECT/deer-flow/frontend/src/components/workspace/settings/model-settings-page.tsx", "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "return (" in line and "const { models, running, isLoading" in lines[i-2]:
        start_idx = i
    if start_idx != -1 and i > start_idx and "function LocalServicesTab" in line:
        end_idx = i - 3
        break

if start_idx != -1 and end_idx != -1:
    new_return = """  return (
    <div className="grid grid-cols-2 gap-6 h-full items-start">
      {/* ---------- 左侧：本地 Ollama ---------- */}
      <div className="space-y-4 pr-2 border-r h-full">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🦙</span>
            <div>
              <p className="font-medium text-sm">Ollama 本地服务器</p>
              <p className="text-xs text-muted-foreground">端口: 11434 (无可配)</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={running ? "default" : "secondary"} className={running ? "bg-green-600 font-normal" : "font-normal"}>
              {running ? "正在运行" : "未运行"}
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
          <div className="text-center py-6 text-muted-foreground border rounded-lg bg-accent/20">
            <p className="text-sm font-medium">Ollama 本地未运行</p>
            <p className="text-xs mt-1">请运行: <code className="bg-muted px-1 py-0.5 rounded font-mono">ollama serve</code></p>
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
                    className={`flex items-center justify-between rounded-lg border p-2 cursor-pointer transition-colors hover:shadow-sm ${isActive ? "border-primary bg-primary/5 shadow-sm" : "hover:border-primary/40 hover:bg-accent/30"}`}
                    onClick={() => {
                      if (!isActive) onSetActive("ollama", m.name);
                    }}
                  >
                    <div className="min-w-0">
                      <p className="font-mono text-sm font-semibold truncate">{m.name}</p>
                      <div className="flex gap-1.5 mt-1 flex-wrap">
                        {m.parameter_size && <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded">{m.parameter_size}</span>}
                        {m.quantization && <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded">{m.quantization}</span>}
                        {m.size_gb > 0 && <span className="text-[10px] bg-muted px-1.5 py-0.5 rounded">{m.size_gb}GB</span>}
                      </div>
                    </div>
                    {isActive ? (
                      <Button variant="default" size="sm" className="h-6 px-2 text-xs bg-primary pointer-events-none shrink-0 transition-opacity ml-2">
                        <CheckIcon className="size-3 mr-1" /> 已激活
                      </Button>
                    ) : (
                      <Button variant="outline" size="sm" className="h-6 px-2 text-xs shrink-0 transition-all opacity-80 hover:opacity-100 hover:border-primary hover:text-primary ml-2" onClick={(e) => { e.stopPropagation(); onSetActive("ollama", m.name); }}>
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
              <p className="font-medium text-sm">Ollama 远程集群</p>
              <p className="text-xs text-muted-foreground">需配置 Host API 等参数</p>
            </div>
          </div>
          {remoteOllama && (
            <Button variant="default" size="sm" onClick={() => setConfiguring(remoteOllama)}>
              {remoteOllama.has_key ? "修改配置" : "开启配置"}
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
                      className={`flex items-center justify-between rounded-lg border p-2 cursor-pointer transition-colors hover:shadow-sm ${isActive ? "border-primary bg-primary/5 shadow-sm" : "hover:border-primary/40 hover:bg-accent/30"}`}
                      onClick={() => {
                        if (!isActive) onSetActive(remoteOllama.id, mName);
                      }}
                    >
                      <p className="font-mono text-sm font-semibold truncate min-w-0 pr-2">{mName}</p>
                      {isActive ? (
                        <Button variant="default" size="sm" className="h-6 px-2 text-xs bg-primary pointer-events-none shrink-0 transition-opacity ml-2">
                          <CheckIcon className="size-3 mr-1" /> 已激活
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm" className="h-6 px-2 text-xs shrink-0 transition-all opacity-80 hover:opacity-100 hover:border-primary ml-2 hover:text-primary" onClick={(e) => { e.stopPropagation(); onSetActive(remoteOllama.id, mName); }}>
                          使用
                        </Button>
                      )}
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          ) : (
            <div className="text-center py-6 border rounded-lg bg-accent/20">
              <p className="text-sm font-medium text-muted-foreground mb-4">云端未就绪或未抓取模型</p>
              <Button variant="outline" size="sm" onClick={() => setConfiguring(remoteOllama)}>
                立即配置并加载远端模型
              </Button>
            </div>
          )
        ) : (
          <div className="text-center py-6 text-muted-foreground text-sm border rounded bg-accent/50">未找到远程节点提供商</div>
        )}
      </div>
    </div>
  );"""
    
    final_lines = lines[:start_idx] + new_return.splitlines() + lines[end_idx+1:]
    with open("/Users/m3max/VS-CODE-PROJECT/deer-flow/frontend/src/components/workspace/settings/model-settings-page.tsx", "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))
    print("Successfully replaced OllamaTab.")
else:
    print("Failed to find indices!")
