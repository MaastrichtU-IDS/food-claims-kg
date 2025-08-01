import re, json

with open("index.html", "r") as f:
    html = f.read()

match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.DOTALL)
if not match:
    print("❌ No JSON-LD found in index.html")
    exit(1)

data = json.loads(match.group(1))
with open("extracted.jsonld", "w") as out:
    json.dump(data, out, indent=2)

print("✅ Saved extracted JSON-LD to extracted.jsonld")
