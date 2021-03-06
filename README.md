# green-signals

## Introduction

green-signals is the source code for "Grüne Signale" digital signage solution.

## Features

"Grüne Signale" offers a digital signage platform intended for use in showrooms.
Main goal is to run a slideshow presenting end-user customizable contents with low efforts and budget required to set it up.

* Low Budget solution
* Low Knowledge requirements
* All based on OpenSource modules and OpenSource itself
* Playback of Images and Videos (muted)
* Media files can be delivered in nested folders
* Playback of Media follows alpabetical order
* Easy to configure
* Easy content updates via media download (zipped)
* Once set up it shall run unattended
* Written in Python 3

## Prerequisites

* Raspberry Pi computer with Power supply, HDMI cable and SD-Card
* Display with HDMI input (best with HDMI CEC support)
* *this can be a dedicated computer monitor or a TV Set*
* *the Display should support FullHD Resolution (native 1920x1080)*
* LAN or WLAN connection
* Mouse and Keyboard only needed for initial setup
* VLC Application (included in Full Raspian Image)
* Python-VLC module (needs to be installed during setup)
* Python-crontab module (needs to be installed
* Cloud account for automated media update (we suggest to use "Grüne Wolke")
* *The media files need to be provided as ZIP-File containing the images and videos*

## Media formats

* Images in JPG or PNG format, same display duration for all images as configured
* Videos in MOV, M4V or MP4 format
* All media shall have 16:9 landscape format
* *media with a different aspect ratio will show black borders*
* All media will be scaled to fill the screen
* Best resolution is 1920x1080 pixels (FullHD)
* *images larger than 1920x1080 are scaled down after download, which is quite slow on the Raspberry Pi*
* Video clips are muted during playback
* Video clips should start and end with blending from/to a black frame (playback could flicker)

## Environmental Topics

* A Raspberry Pi computer has low energy consumption (usually less than 10W)
* It can be configured for a safe shut down at night time (reduce light pollution)
* A diplay supporting HDMI CEC will automatically switch to StandBy
* Power for Raspberry Pi and display shall be turned off by a timer device
* *set the timer a few minutes after scheduled shut down of the Raspberry Pi computer*
* when the power is switched back on in the morning, The slideshow will autoomatically start and in background update the media files

## Development Environment

* The project is developed on a Raspberry Pi 400, any Raspberry Pi model (except Pico) is fine
* Raspberry Pi 1 and Zero models may partially work (limitatons with video playback)
* The project is intended to run on "Raspberry Pi OS" (based on Debian Buster)
* *support for other platforms is possible, but not tested*

## TODOs

- [x] create setup script *(setup.py)*
- [x] 	 run pip3 install python-vlc
- [x] 	 run pip3 install python-crontab
- [x]    add green-signals to auto-start
- [x]    write configuration file
- [x]    user friendly GUI
- [x] configuration script *(included in setup.py)*
- [x]    add cronjob for safe shutdown at given time *(obsolete, handled internally)*
- [ ]    validation that remote URL points to a ZIP file.
- [ ] improve on-barding
- [ ]    so far only dummy images for intial slideshow
- [ ]    provide manual in media slides and as documentation (Wiki?)
- [ ]    tutorials and other on-boarding guides (maybe with "Grünstreifen")
- [ ] testing, testing
- [ ]    and more testing in real world ;-)

## Contact:
Chatbegruenung, Channel netzbegruenung-digitalsignage
Stefan Schmidt-Bilkenroth, ssb@mac.com
