#! /bin/sh

npm install && 
mv ./build/Release/rgb565.node ../../utils/rgb565.node &&
rm -r node_modules build package-lock.json

