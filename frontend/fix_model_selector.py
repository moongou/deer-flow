with open("/Users/m3max/VS-CODE-PROJECT/deer-flow/frontend/src/components/ModelSelector.tsx", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(r"\n", "\n")

with open("/Users/m3max/VS-CODE-PROJECT/deer-flow/frontend/src/components/ModelSelector.tsx", "w", encoding="utf-8") as f:
    f.write(text)

