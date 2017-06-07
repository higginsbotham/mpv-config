#!/bin/bash
brew reinstall --without-harfbuzz libass
brew reinstall --with-rtmpdump --with-openssl --with-libass --with-libbs2b --with-rubberband ffmpeg
brew reinstall --with-vapoursynth --with-rubberband --with-libarchive --with-bundle mpv
brew reinstall mvtools
brew reinstall ffms2
brew reinstall subliminal
brew linkapps mpv