## Summary

This is a gateway routing IBUS-messages from the LIN-bus interface to TCP/IP clients 
*(KODI/XBMC, HTTP, etc)*. This is aimed to be built on a Linux-platform using `cmake`, hence 
configurations is explicitly only for Linux-platforms.

### 1. Preparation

- Install cmake
- Install cross-compiler *(for Raspberry Pi)*
- Install and compile boost-libraries *(for each platform)*
- Adjust `BOOST_INCLUDEDIR` and `BOOST_LIBRARYDIR` accordingly in `CMakeLists.txt`

### 2a. Build - Manually

```bash
# Create build path
mkdir build
cd build/

# Create makefiles and compile project
cmake ../
make
```

### 2b. Build - From Netbeans

Create project in Netbeans: `File -> New project`
1. Under "Choos Project" select `C/C++ Project with Existing Source`
2. Under "Select Mode" browse to source and `Select Configuration Mode -> Custom`
3. Under "Build Tool" check `Run Configure Script in Subfolder`
4. Under "Build Actions" specify where the built executable should be placed in `Build Result` *(optional)*
5. -7. Use Default Settings. Press "Finish" and a build is performed.

### 3. Run

```bash
# IBUS-interface <USB-interface> below is usually /dev/ttyUSB0
sudo ./gateway -d <USB-interface> -i 0.0.0.0
```

## Reference

Project is forked from https://github.com/cgart/OpenBM.  

Please see [Wiki](http://git.one-infiniteloop.com/larsa/bmw-infotainment/wikis/home) for how to install cmake and cross-compiler