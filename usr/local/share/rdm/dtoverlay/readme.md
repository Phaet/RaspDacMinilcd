
# Building the overlay
```
sudo dtc -@ -I dts -O dtb -o ili9341.dtbo /usr/local/share/rdm/dtoverlay/ili9341.dts
```

# Installing the overlay
```
sudo mv ili9341.dtbo /boot/firmware/overlays/
```

# Editing config.txt
```
grep -qxF "dtoverlay=ili9341" /boot/firmware/config.txt || echo -e "dtoverlay=ili9341" | sudo tee -a /boot/firmware/config.txt > /dev/null
```