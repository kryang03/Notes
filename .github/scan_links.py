import os, re, glob

BASE = "/Users/yang/Notes/Notes"

# Collect all existing note names (without extensions)
all_notes = set()
for folder in ['Foundations', 'PapersRecap', 'Projects/Dynamic Non-Prehensile Manipulation']:
    full = os.path.join(BASE, folder)
    for f in glob.glob(os.path.join(full, '*.md')):
        all_notes.add(os.path.splitext(os.path.basename(f))[0])

# Scan all markdown files for wikilinks
broken = []
for folder in ['Foundations', 'PapersRecap', 'Projects/Dynamic Non-Prehensile Manipulation']:
    full = os.path.join(BASE, folder)
    for filepath in glob.glob(os.path.join(full, '*.md')):
        with open(filepath, 'r') as f:
            content = f.read()
        links = re.findall(r'\[\[([^\]|#]+?)(?:#[^\]|]*)?(?:\|[^\]]*?)?\]\]', content)
        for link in links:
            link = link.strip()
            if link.endswith(('.pdf', '.png', '.jpg', '.txt', '.base')):
                continue
            if link not in all_notes:
                broken.append((os.path.basename(filepath), link))

seen = set()
for src, target in sorted(broken):
    key = (src, target)
    if key not in seen:
        seen.add(key)
        print(f"BROKEN: [{src}] -> [[{target}]]")

if not seen:
    print("No broken wikilinks found!")
else:
    print(f"\nTotal: {len(seen)} broken links")
