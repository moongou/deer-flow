with open("/Users/m3max/VS-CODE-PROJECT/deer-flow/frontend/src/components/workspace/settings/model-settings-page.tsx", "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

for i, line in enumerate(lines):
    if "未找到远程节点提供商</div>" in line:
        # inject } after );
        # locate );
        pass

# let's just do a sed or something
content = "\n".join(lines)
content = content.replace("    </div>\n  );\n// ---------------------------------------------------------------------------", "    </div>\n  );\n}\n// ---------------------------------------------------------------------------")

with open("/Users/m3max/VS-CODE-PROJECT/deer-flow/frontend/src/components/workspace/settings/model-settings-page.tsx", "w", encoding="utf-8") as f:
    f.write(content)
