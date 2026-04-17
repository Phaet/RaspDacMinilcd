
## RDMLCD on moOde Audio 10.x

### Disclaimer

This branch is still being tested

### Summary  
• This branch contains a version of the RaspDacMiniLCD package for moOde10  
• 64bit version only (32bit not supported)  
• No pre-compiled binaries : some dependencies have to be downloaded and compiled directly on the pi.  
• Bumped node-canvas dependency to canvas 3.0.0.  
• No longer uses the now-obsoleted fbcp-ili9341, but uses a custom dtoverlay with preconfigured init sequence instead (more maintainable but less performant)  
• Added some adjustments to follow some change in moOde system since version 8 (mpd volume value is no longer an accurate representation of user-defined volume)  
• Supports now also track cover images sent by radio stations with the stream.9  
• Included a compile procedure directly in the npm package for the display renderer to help with native dependencies that have to be compiled.  

### Installation

This walkthrough assumes you are working on a fresh moOde 9 installation with a wired network. I did test on a pi4 so far. It is very likely that it will work on a pi3 as well.

1. Connect to your RDMLCD using SSH

Please refer to this guide if you have trouble setting up your moOde install with SSH enabled. Once you are in, start by updating apt

```sudo apt-get update -y```



2. Get and install project files

```
wget https://github.com/audiophonics/RaspDacMinilcd/archive/refs/heads/moode9.tar.gz
tar -xvf moode9.tar.gz
sudo rsync -a RaspDacMinilcd-moode9/usr/ /usr/
```


3. Compile and install dtoverlay

This is the main part that replaces fbcp-ili9341, you can inspect the source file here . Be careful as this will write into /boot/firmware/config.txt and add a dts file into /boot/firmware/overlays/

```
sudo dtc -@ -I dts -O dtb -o ili9341.dtbo /usr/local/share/rdm/dtoverlay/ili9341.dts
sudo mv ili9341.dtbo /boot/firmware/overlays/
grep -qxF "dtoverlay=ili9341" /boot/firmware/config.txt || echo -e "dtoverlay=ili9341" | sudo tee -a /boot/firmware/config.txt > /dev/null
```


4. Compile and install RDMLCD renderer

Get build dependencies

```
sudo apt-get install --no-install-recommends -y nodejs npm jq libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev
```



Compile native addons and get node_modules

This part can take a while because it needs to compile a light version of cairo for image generation.

```
cd /usr/local/etc/rdmlcd
npm install 
cd
```


Enable renderer service to run at boot

```
sudo systemctl enable /usr/local/etc/rdmlcd/service/rdmlcd.service
```


5. Download and configure LIRC

Download LIRC

```
sudo apt-get install --no-install-recommends -y lirc
```


Disable LIRC default service and provide our own config instead

```
sudo systemctl daemon-reload
sudo systemctl enable /usr/local/etc/rdmlcdremote/service/arm64/rdmlcdlirc.service
sudo systemctl enable /usr/local/etc/rdmlcdremote/service/rdmlcdirexec.service 
sudo systemctl disable lircd irexec
sudo systemctl stop lircd irexec
```


Edit /boot/firmware/config.txt to enable gpio-ir at boot

```
grep -qxF "dtoverlay=gpio-ir,gpio_pin=4" /boot/firmware/config.txt || echo -e "dtoverlay=gpio-ir,gpio_pin=4" | sudo tee -a /boot/firmware/config.txt > /dev/null
```


6. Configure DAC and Reboot

bc is needed to allow cycling alsa properties from within apessq2m shell script

```
sudo apt-get install --no-install-recommends -y bc
```


After this is done, you still need to configure moode.local/snd-config.php
• select Audiophonics ES9028/9038 DAC as option for Named I2S device 
• reboot
•  Volume type should be set to hardware after reboot to achieve best sound quality if you need to control volume directly from moOde (no preamp after the rdmlcd)

