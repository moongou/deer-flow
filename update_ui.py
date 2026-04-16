import re

with open("frontend/src/components/workspace/settings/model-settings-page.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update TabsList make it sticky
content = content.replace('TabsList className="w-full shrink-0 grid grid-cols-4 mb-4"', 'TabsList className="sticky top-0 z-10 w-full shrink-0 grid grid-cols-4 mb-4 bg-background"')

# 2. Layout of ProviderCard
card_original = """          <Card
            className={`cursor-pointer transition-all hover:shadow-md hover:border-primary/40 ${
              active ? "border-primary ring-1 ring-primary/30" : ""
            } ${provider.enabled ? "" : "opacity-80"}`}
            onClick={() => onConfigure(provider)}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-2xl shrink-0">{provider.icon}</span>
                  <div className="min-w-0">
                    <p className="font-semibold text-sm truncate">{provider.name}</p>
                    <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5" title={provider.description}>
                      {provider.description}
                    </p>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1.5 shrink-0">
                  {provider.has_key && <Badge variant="default" className="bg-green-600">已配置</Badge>}
                  {active && <Badge variant="outline" className="border-primary text-primary">已部署</Badge>}
                </div>
              </div>
            </CardContent>
          </Card>"""

card_new = """          <Card
            className={`cursor-pointer transition-all hover:shadow-sm hover:border-primary/40 ${
              active ? "border-primary ring-1 ring-primary/30" : ""
            } ${provider.enabled ? "" : "opacity-80"}`}
            onClick={() => onConfigure(provider)}
          >
            <CardContent className="p-2.5">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xl shrink-0">{provider.icon}</span>
                  <div className="min-w-0">
                    <p className="font-medium text-sm truncate">{provider.name}</p>
                    <p className="text-[10px] text-muted-foreground truncate" title={provider.description}>
                      {provider.description}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  {provider.has_key && <Badge variant="default" className="bg-green-600 text-[10px] px-1 py-0 h-4">已配</Badge>}
                  {active && <Badge variant="outline" className="border-primary text-primary text-[10px] px-1 py-0 h-4">部署</Badge>}
                </div>
              </div>
            </CardContent>
          </Card>"""
content = content.replace(card_original, card_new)

# 3. Two columns for providers tab
old_groups_map = """                    ) : (
                      groups.map((g) => {
                        const list = byGroup[g];
                        if (!list?.length) return null;
                        const meta = GROUP_LABELS[g];
                        return (
                          <div key={g}>
                            <div className="flex items-center gap-2 mb-3">
                              <span className="text-base">{meta.emoji}</span>
                              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                                {meta.label}
                              </h3>
                              <Separator className="flex-1" />
                            </div>
                            <div className="grid grid-cols-1 gap-2">
                              {list.map((p) => (
                                <ProviderCard
                                  key={p.id}
                                  provider={p}
                                  active={active.active_provider === p.id}
                                  onConfigure={setConfiguring}
                                />
                              ))}
                            </div>
                          </div>
                        );
                      })
                    )}"""

new_groups_map = """                    ) : (
                      <div className="grid grid-cols-2 gap-6 items-start">
                        <div className="space-y-6">
                          {["international", "local", "custom"].map((g) => {
                            const list = byGroup[g as keyof typeof byGroup];
                            if (!list?.length && g !== "custom") return null;
                            const meta = GROUP_LABELS[g as keyof typeof GROUP_LABELS];
                            return (
                              <div key={g}>
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-base">{meta?.emoji}</span>
                                  <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                                    {meta?.label}
                                  </h3>
                                  <Separator className="flex-1" />
                                </div>
                                <div className="grid grid-cols-1 gap-2">
                                  {list?.map((p) => (
                                    <ProviderCard
                                      key={p.id}
                                      provider={p}
                                      active={active.active_provider === p.id}
                                      onConfigure={setConfiguring}
                                    />
                                  ))}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        <div className="space-y-6">
                          {["china"].map((g) => {
                            const list = byGroup[g as keyof typeof byGroup];
                            if (!list?.length) return null;
                            const meta = GROUP_LABELS[g as keyof typeof GROUP_LABELS];
                            return (
                              <div key={g}>
                                <div className="flex items-center gap-2 mb-2">
                                  <span className="text-base">{meta?.emoji}</span>
                                  <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                                    {meta?.label}
                                  </h3>
                                  <Separator className="flex-1" />
                                </div>
                                <div className="grid grid-cols-1 gap-2">
                                  {list?.map((p) => (
                                    <ProviderCard
                                      key={p.id}
                                      provider={p}
                                      active={active.active_provider === p.id}
                                      onConfigure={setConfiguring}
                                    />
                                  ))}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}"""
content = content.replace(old_groups_map, new_groups_map)


with open("frontend/src/components/workspace/settings/model-settings-page.tsx", "w", encoding="utf-8") as f:
    f.write(content)

