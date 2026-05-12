import os
import subprocess
import sys

# ── Core dependencies ──────────────────────────────────────────────
print("Installing core requirements...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

# ── Playwright browsers ────────────────────────────────────────────
print("Installing Playwright browsers...")
subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)

# ── Optional: detect what user wants ──────────────────────────────
args = sys.argv[1:]
extras = []

if "--extras" in args:
    idx = args.index("--extras")
    extras = args[idx + 1].split(",") if idx + 1 < len(args) else []
elif "--all" in args:
    extras = ["gestures", "ai", "ac", "cloud", "windows", "security"]

if extras:
    print(f"\nInstalling optional features: {', '.join(extras)}")

    optional_packages = {
        "gestures": [
            "tensorflow>=2.15.0",
            "scikit-learn>=1.3.0",
            "mediapipe>=0.10.0",
            "imutils>=0.5.4",
        ],
        "ai": [
            "langchain>=1.2.0",
            "langchain-core>=1.3.0",
            "langgraph>=1.1.0",
            "tiktoken>=0.7.0",
            "sentence-transformers>=3.0.0",
            "huggingface-hub>=0.24.0",
            "datasets>=2.14.0",
        ],
        "ac": [
            "broadlink>=0.18.0",
            "pydaikin>=2.7.0",
            "pymelcloud>=0.1.0",
            "aircloudy>=0.1.0",
            "thinq2>=0.5.0",
        ],
        "cloud": [
            "boto3>=1.34.0",
            "azure-core>=1.30.0",
            "azure-identity>=1.17.0",
            "azure-storage-blob>=12.22.0",
            "redis>=5.0.0",
            "rq>=2.0.0",
        ],
        "windows": [
            "pywin32>=306",
            "pywinauto>=0.6.8",
            "win10toast>=0.9",
            "pygetwindow>=0.0.9",
            "pycaw>=0.0.5",
            "comtypes>=1.4.0",
        ],
        "security": [
            "dnspython>=2.6.0",
            "cryptography>=42.0.0",
        ],
    }

    for extra in extras:
        extra = extra.strip().lower()
        if extra in optional_packages:
            pkgs = optional_packages[extra]
            print(f"\n  [{extra}] Installing {len(pkgs)} packages...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install"] + pkgs,
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print(f"  [{extra}] ✅ Done")
            else:
                # Extract failed package from error
                for line in result.stderr.split("\n"):
                    if "ERROR" in line or "could not find" in line.lower():
                        print(f"  [{extra}] ⚠ {line.strip()}")
                        break
                else:
                    print(f"  [{extra}] ⚠ Some packages failed (may need Python 3.12)")
        else:
            print(f"\n  [{extra}] Unknown group. Available: {', '.join(optional_packages.keys())}")

# ── Download agent personas ────────────────────────────────────────
print("\nDownloading agency-agent expert personas...")
download_script = os.path.join(os.path.dirname(__file__), "scripts", "download_agents.py")
if os.path.exists(download_script):
    subprocess.run([sys.executable, download_script], check=False)
else:
    print(f"  Warning: {download_script} not found, skipping agent download.")

# ── Done ───────────────────────────────────────────────────────────
print("\n" + "=" * 50)
print("✅ Setup complete! Run 'python main.py' to start FRIDAY.")
print()
if not extras:
    print("💡 Optional features not installed. To add them later:")
    print("   python setup.py --extras gestures    # Hand gesture control (Python 3.12)")
    print("   python setup.py --extras ai           # AI pipeline + vector memory")
    print("   python setup.py --extras ac           # AC control (LG, Daikin, etc.)")
    print("   python setup.py --extras cloud        # AWS + Azure")
    print("   python setup.py --extras windows      # Windows-specific features")
    print("   python setup.py --extras security     # DNS + crypto for cyber tools")
    print("   python setup.py --all                 # Everything")
    print()
    print("   Or install manually:")
    print("   pip install -r requirements-optional.txt")
