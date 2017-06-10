#!/bin/bash
brew reinstall --without-harfbuzz libass
brew reinstall --with-rtmpdump --with-openssl --with-libass --with-libbs2b --with-rubberband --with-tesseract --with-fdk-aac --with-libbs2b --with-libsoxr --with-libvidstab --with-libvorbis --with-libvpx --with-opus --with-sdl2 --with-tools --with-x265 ffmpeg
brew reinstall --with-vapoursynth --with-rubberband --with-libarchive --with-bundle mpv
brew reinstall mvtools
brew reinstall ffms2
brew reinstall subliminal
brew linkapps mpv
