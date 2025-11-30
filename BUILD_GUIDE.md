# Backend Build and Distribution Guide

## Overview

This guide explains how to build, test, and distribute the packaged backend executable (`backend.exe`) for the Comet Task Runner.

---

## Prerequisites

- **Python 3.x** installed on your development machine
- **All dependencies** installed: `pip install -r requirements.txt`
- **PyInstaller**: Will be auto-installed by `build_backend.bat`

---

## Building backend.exe

### Quick Build

Simply run the build script:

```batch
build_backend.bat
```

The script will:
1. Check/install PyInstaller
2. Clean previous builds
3. Run PyInstaller with `backend.spec`
4. Show build results and file size

### Manual Build

If you prefer manual control:

```batch
# Install PyInstaller
pip install pyinstaller

# Build using spec file
pyinstaller backend.spec

# Output will be in dist/backend.exe
```

### Build Configuration

The build is configured in `backend.spec`:

| Option | Value | Purpose |
|--------|-------|---------|
| `console` | `True` | Show console for logging |
| `onefile` | ✅ | Single .exe file |
| `upx` | `True` | Compress with UPX (~30% smaller) |
| `hiddenimports` | Many modules | Include all dependencies |
| `excludes` | tkinter, matplotlib | Reduce size |

**Expected Output Size**: 120-180MB (varies based on dependencies)

---

## Testing the Packaged Executable

### Test 1: Standalone Execution

```batch
# Navigate to dist folder
cd dist

# Run backend.exe directly (no Python needed)
backend.exe
```

**Expected Output**:
```
============================================================
Starting Comet Task Runner Backend
============================================================
✓ TaskQueue initialized with Comet path: C:\...\comet.exe
URL Task API: POST /execute/url
AI Task API:  POST /execute/ai
============================================================
 * Running on http://127.0.0.1:5000
```

### Test 2: Health Check

With backend running, open another terminal:

```batch
curl http://127.0.0.1:5000/health
```

**Expected**: `{"status":"ok","message":"Comet Task Runner is running"}`

### Test 3: URL Task

```batch
curl -X POST http://127.0.0.1:5000/execute/url ^
  -H "Content-Type: application/json" ^
  -d "{\"url\":\"https://www.google.com\"}"
```

**Expected**: Comet browser should launch and open Google

### Test 4: Full Integration

```batch
# Start with the packaged backend
start.bat
```

The script should:
1. Detect `dist\backend.exe` exists
2. Prefer using the .exe over Python script
3. Launch frontend and backend in separate terminals

---

## Distribution to End Users

### Option A: Simple ZIP Distribution

1. **Package files**:
   ```
   comet-taskrunner-v0.2.0/
   ├── dist/
   │   └── backend.exe          ← Packaged backend
   ├── src/
   │   └── frontend.py           ← Frontend (needs Python)
   ├── requirements.txt          ← For frontend only
   ├── start.bat                 ← Smart launcher
   └── README.md
   ```

2. **ZIP and distribute**

3. **User setup**:
   - Install Python 3.x
   - Run: `pip install -r requirements.txt`
   - Double-click: `start.bat`

### Option B: Advanced - Installer

Create a professional installer using **Inno Setup**:

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Create `installer.iss` script (template below)
3. Compile to `.exe` installer

**Benefits**:
- One-click installation
- Automatic Python detection
- Desktop shortcuts
- Uninstaller

---

## Updating Dependencies and Rebuilding

### When to Rebuild

Rebuild `backend.exe` when you:
- Update Python dependencies in `requirements.txt`
- Modify backend code (`src/backend.py`, `src/tasks/*`, etc.)
- Fix bugs in automation logic

### Update Workflow

```batch
# 1. Update code/dependencies
git pull
pip install -r requirements.txt

# 2. Test with Python first
python src/backend.py

# 3. Rebuild executable
build_backend.bat

# 4. Test packaged version
dist\backend.exe

# 5. Commit and tag
git add dist/backend.exe
git commit -m "build: Update backend.exe to v0.2.1"
git tag v0.2.1
git push --tags
```

---

## Common Issues and Solutions

### Issue 1: Windows Defender Flags backend.exe

**Cause**: PyInstaller executables are sometimes flagged as false positives

**Solutions**:
1. **For developers**: Add exception in Windows Defender
   - Settings → Virus & threat protection → Exclusions
   - Add `dist\backend.exe`

2. **For distribution**: Submit to Microsoft for analysis
   - https://www.microsoft.com/en-us/wdsi/filesubmission

3. **Alternative**: Code-sign the executable
   - Requires a code signing certificate (~$100/year)
   - Significantly reduces false positives

### Issue 2: Missing DLL Errors

**Error**: `The code execution cannot proceed because X.dll was not found`

**Solution**:
1. Install Visual C++ Redistributables:
   - https://aka.ms/vs/17/release/vc_redist.x64.exe

2. Add missing DLLs to `backend.spec`:
   ```python
   binaries=[
       ('C:\\path\\to\\missing.dll', '.'),
   ],
   ```

### Issue 3: Large File Size

Current size: ~120-180MB

**Reduction strategies**:

1. **UPX Compression** (already enabled):
   - Reduces size by ~30%

2. **Exclude unused modules** in `backend.spec`:
   ```python
   excludes=[
       'tkinter',
       'matplotlib',  
       'pandas',
       # Add more unused modules
   ],
   ```

3. **Remove debugging symbols**:
   ```python
   strip=True,  # Remove symbols
   ```

4. **Use --onedir** instead of --onefile:
   - Faster startup
   - Slightly larger (~200MB folder)
   - Better for local installation

### Issue 4: Import Errors When Running .exe

**Error**: `ModuleNotFoundError: No module named 'X'`

**Solution**: Add to `hiddenimports` in `backend.spec`:
```python
hiddenimports=[
    'X',  # Add the missing module
    'X.submodule',
],
```

---

## Version Management Strategy

### Semantic Versioning

Use `MAJOR.MINOR.PATCH` format:
- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

**Example**: `0.2.1`
- 0 = Pre-release
- 2 = Second feature release
- 1 = First patch

### Release Checklist

- [ ] Update version in `README.md`
- [ ] Update version in `backend.py` (if applicable)
- [ ] Rebuild `backend.exe`
- [ ] Test all API endpoints
- [ ] Test full UI workflow
- [ ] Update `CHANGELOG.md`
- [ ] Git tag: `git tag v0.2.1`
- [ ] Push: `git push --tags`
- [ ] Create GitHub Release with:
  - Release notes
  - `backend.exe` attachment
  - Full project ZIP

---

## Continuous Maintenance

### Monthly Tasks

- [ ] Review and merge dependabot PRs
- [ ] Update Python dependencies: `pip-review --auto`
- [ ] Rebuild and test `backend.exe`
- [ ] Check for new Windows/Comet compatibility issues

### Quarterly Tasks

- [ ] Review PyInstaller updates
- [ ] Test on fresh Windows installation
- [ ] Update documentation
- [ ] Gather user feedback

---

## Advanced: GitHub Actions Auto-Build

Automate building on every release:

```yaml
# .github/workflows/build.yml
name: Build Backend

on:
  release:
    types: [created]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: pyinstaller backend.spec
      - uses: actions/upload-artifact@v2
        with:
          name: backend.exe
          path: dist/backend.exe
```

---

## Support and Troubleshooting

If you encounter issues not covered here:

1. Check PyInstaller docs: https://pyinstaller.org/
2. Review build logs in `build/backend/`
3. Open an issue on GitHub with:
   - Error message
   - Build log
   - Windows version
   - Python version

---

**Last Updated**: 2025-11-29  
**Maintainer**: Barry  
**PyInstaller Version**: 6.x+
