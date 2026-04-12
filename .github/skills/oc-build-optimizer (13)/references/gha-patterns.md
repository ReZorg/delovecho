# GitHub Actions Workflow Patterns for org-oc

> Auto-generated from build model (iteration 5). Last updated: 2026-03-10T01:44:32.382920+00:00

## Container Strategy

Two proven approaches exist for org-oc CI:

**Option A: opencog/opencog-deps container** (from config.yml / CircleCI)
- Pre-installed system dependencies, fastest cold start
- Use `image: opencog/opencog-deps` with `--user root`
- Includes Guile, Boost, CxxTest, Python bindings

**Option B: ubuntu:22.04 bare** (from consolidated-build)
- More control, explicit dependency installation
- Requires `apt-get install` step per job
- Better for debugging dependency issues

Recommended: Use opencog-deps for the main build, bare ubuntu for validation.

## System Packages (Consolidated)

All system packages required across all components:

```bash
sudo apt-get install -y \
  autoconf \
  automake \
  binutils-dev \
  cmake \
  cxxtest \
  cython3 \
  guile-3.0-dev \
  libboost-all-dev \
  libiberty-dev \
  liboctomap-dev \
  libopencv-dev \
  libopenmpi-dev \
  libpqxx-dev \
  librocksdb-dev \
  libssl-dev \
  libtool \
  swig \
  unixodbc-dev \
```

## Artifact Passing Pattern

Each component uploads its install artifacts for downstream jobs:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: <component>-install
    path: |
      /usr/local/include/opencog
      /usr/local/lib/opencog
      /usr/local/lib/cmake
      /usr/local/share/opencog
```

Downstream jobs download and restore:

```yaml
- uses: actions/download-artifact@v4
  with:
    name: <dep>-install
    path: /tmp/<dep>-install
- run: sudo cp -r /tmp/<dep>-install/* / && sudo ldconfig
```

## Known Build Fixes (Auto-Accumulated)

Fixes discovered through iterative diagnosis:

1. **atomspace missing lib/ directory**: Create `mkdir -p lib && echo '# Build compatibility' > lib/CMakeLists.txt`
2. **Cython version mismatch**: Always `pip install --upgrade cython` before building Python bindings
3. **ldconfig after install**: Every `sudo make install` must be followed by `sudo ldconfig`
4. **opencog/lib path**: Add `echo "/usr/local/lib/opencog" | sudo tee /etc/ld.so.conf.d/opencog.conf`
5. **Boost discovery**: Set `-DBOOST_ROOT` and `-DCMAKE_PREFIX_PATH` when using conda-based Boost
6. **atomspace-storage prerequisite**: Many atomspace-* extensions require atomspace-storage installed first
7. **asmoses**: [asmoses] sys_dep libmpi-dev → libopenmpi-dev
8. **moses**: [moses] sys_dep libmpi-dev → libopenmpi-dev
