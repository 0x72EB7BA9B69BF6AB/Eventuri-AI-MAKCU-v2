import sys
import os

def get_site_packages():
    """Try to get the actual site-packages folder in this venv, cross-platform."""
    # Try standard venv structure first (Windows & Linux/Mac)
    candidates = [
        os.path.join(sys.prefix, "Lib", "site-packages"),   # Windows venv
        os.path.join(sys.prefix, "lib", "python%s.%s" % sys.version_info[:2], "site-packages") # Linux/mac venv
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    # As fallback, try user site
    try:
        import site
        return site.getusersitepackages()
    except Exception:
        return None

# If you want to force the path, uncomment the line below:
# site_packages = r"C:\Eventuri Ai\Final\tt\venv\Lib\site-packages"
site_packages = get_site_packages()
ultralytics_dir = os.path.join(site_packages, "ultralytics")
print(f"[*] Using ultralytics path: {ultralytics_dir}")

# --- PATCHING RULES ---
patches = [
    {
        "file": "engine/exporter.py",
        "replacements": [
            {
                "pattern": '"onnxruntime-gpu" if cuda else "onnxruntime"',
                "replacement": '"onnxruntime-directml" if cuda else "onnxruntime-directml"'
            },
            {
                "pattern": 'requirements += ["onnxslim>=0.1.59", "onnxruntime" + ("-gpu" if torch.cuda.is_available() else "")]',
                "replacement": 'requirements += ["onnxslim>=0.1.59", "onnxruntime" + ("-directml" if torch.cuda.is_available() else "")]'
            },
        ]
    },
    {
        "file": "nn/autobackend.py",
        "replacements": [
            {
                "pattern": 'check_requirements(("onnx", "onnxruntime-gpu" if cuda else "onnxruntime"))',
                "replacement": 'check_requirements(("onnx", "onnxruntime-directml" if cuda else "onnxruntime-directml"))'
            },
            {
                "pattern": 'providers = ["CPUExecutionProvider"]',
                "replacement": 'providers = ["DmlExecutionProvider", "CPUExecutionProvider"]'
            },
            {
                "pattern": 'session = onnxruntime.InferenceSession(w, session_options, providers=["CPUExecutionProvider"])',
                "replacement": 'session = onnxruntime.InferenceSession(w, session_options, providers=["DmlExecutionProvider", "CPUExecutionProvider"])'
            },
        ]
    }
]

# --- PATCHING ENGINE ---
for patch in patches:
    target_file = os.path.join(ultralytics_dir, patch["file"].replace("/", os.sep))
    if not os.path.exists(target_file):
        print(f"[!] File not found: {target_file}")
        continue

    print(f"[*] Patching: {target_file}")

    with open(target_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    patched = False
    new_lines = []
    for line in lines:
        for rep in patch["replacements"]:
            if rep["pattern"] in line:
                print(f"    [+] Replacing: {rep['pattern']} -> {rep['replacement']}")
                line = line.replace(rep["pattern"], rep["replacement"])
                patched = True
        new_lines.append(line)

    if patched:
        with open(target_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"[*] File patched: {target_file}")
    else:
        print(f"[?] No matching patterns found in {target_file} (already patched?)")

print("[+] Done!")
