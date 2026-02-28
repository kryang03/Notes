import os, re, glob

BASE = "/Users/yang/Notes/Notes"

# Build heading index for all files
heading_index = {}  # {filename_no_ext: set of headings}
for folder in ['Foundations', 'PapersRecap', 'Projects/Dynamic Non-Prehensile Manipulation']:
    full = os.path.join(BASE, folder)
    for filepath in glob.glob(os.path.join(full, '*.md')):
        name = os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath, 'r') as f:
            content = f.read()
        headings = set()
        for line in content.split('\n'):
            m = re.match(r'^(#{1,6})\s+(.+)$', line)
            if m:
                headings.add(m.group(2).strip())
        heading_index[name] = headings

# Scan for section-level wikilinks
broken_sections = []
for folder in ['Foundations', 'PapersRecap', 'Projects/Dynamic Non-Prehensile Manipulation']:
    full = os.path.join(BASE, folder)
    for filepath in glob.glob(os.path.join(full, '*.md')):
        with open(filepath, 'r') as f:
            content = f.read()
        # Match [[File#Section]] or [[File#Section|Alias]]
        links = re.findall(r'\[\[([^\]|#\\]+?)#([^\]|\\]+?)(?:\|[^\]]*?)?\]\]', content)
        for target_file, section in links:
            target_file = target_file.strip()
            section = section.strip()
            if target_file in heading_index:
                if section not in heading_index[target_file]:
                    broken_sections.append((os.path.basename(filepath), target_file, section))

seen = set()
for src, target, section in sorted(broken_sections):
    key = (src, target, section)
    if key not in seen:
        seen.add(key)
        print(f"BROKEN SECTION: [{src}] -> [[{target}#{section}]]")

if not seen:
    print("No broken section-level links found!")
else:
    print(f"\nTotal: {len(seen)} broken section links")
