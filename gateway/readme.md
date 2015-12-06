## Summary

This gateway routing IBUS-messages from the LIN-bus interface to TCP/IP clients 
*(KODI/XBMC, HTTP, etc)*. This is aimed to be built on a Linux-platform using `cmake`, hence 
configurations is explicitly only for Linux-platforms.

### 1. Preparation

- Install cmake
- Install cross-compiler *(for Raspberry Pi)*
- Install and compile boost-libraries *(for each target)*
- Adjust `BOOST_LIBRARYDIR` accordingly in `CMakeLists.txt`

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
# Default <USB-interface> = /dev/ttyUSB0
sudo ./openbm-gateway --device=<USB-interface> --address=0.0.0.0
```

## Reference

Project is forked from https://github.com/cgart/OpenBM.

Please see [Wiki](http://git.one-infiniteloop.com/larsa/bmw-infotainment/wikis/home) for how to install cmake and cross-compiler
