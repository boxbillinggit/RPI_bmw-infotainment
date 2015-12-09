## Summary

This is the sources of `libguicallback.so`. The library acts like an interface between the service -and  the script. The reason this module exists is because there's no other way for the service.py to receive GUI-callbacks. Calling a script from XBMC/KODI launches a separate python-interpreter - isolated from service.py. Hence the need of a cPython-plugin routing callbacks between the separate python-interpreters.

### 1. Preparation

- Install cmake
- Install cross-compiler *(for Raspberry Pi)*
- Install `python-dev` *(python-headers and libraries)*

### 2. Configure Netbeans

Create project in Netbeans: `File -> New project`
1. Under "Choos Project" select `C/C++ Project with Existing Source`
2. Under "Select Mode" browse to source and `Select Configuration Mode -> Custom`
3. Under "Build Tool" check `Run Configure Script in Subfolder`
4. Under "Build Actions" specify where the built executable should be placed in `Build Result` *(optional)*
5. -7. Use Default Settings. Press "Finish" and a build is performed.

### 3a. Build - Local host

```bash
./build-i386-linux-gnu.sh
```

### 3b. Build - Target host (Raspberry Pi)

```bash
./build-arm-linux-gnueabihf.sh
```

### 4. Run

```bash
# Test library
python 
>>> import libguicallback
>>> dir(libguicallback)
```

