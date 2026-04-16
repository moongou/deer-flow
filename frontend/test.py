with open("/Users/m3max/VS-CODE-PROJECT/deer-flow/frontend/src/components/workspace/settings/model-settings-page.tsx", "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

for i, line in enumerate(lines[-30:]):
    print(i, line)
