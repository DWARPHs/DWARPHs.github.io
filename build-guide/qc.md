[computer]:Parts.yaml#computer
[USB-C data cable]:Parts.yaml#usb_c
# Check the device (QC)

{{BOM}}

A new device runs only once it has passed DWARPH-QC: a guided check of every part of the
device, done over the USB cable, with no network.

## Run the check {pagestep}

With the device on the [USB-C data cable]{Qty: 1, Cat: tool} and the
[computer]{Qty: 1, Cat: tool}:

```bash
pip install pyserial pillow numpy
python tools/dwarph_qc/dwarph_qc.py
```

It goes through ten steps and asks you to confirm what you see: the device's name on the
display; the coin cell, SD card, cables, antenna, ring and label; the clock; the SD card's
speed; the temperature sensors; the heater; the red, blue and white lights ramping up; the
schedule; a test picture under the capture light; the Wi-Fi.

## Mark it as QC'd {pagestep}

If every step passed, answer **yes** to "Mark this device as QC'd?". The device stores the
result and restarts into normal operation. Keep the report (`qc_reports/`) with the device's
records.

> **Status:** the QC tool is ready; the firmware side is being written (`dwarph-qc` branch of
> DWARPH-firmware). See its `tools/dwarph_qc/README.md`.
