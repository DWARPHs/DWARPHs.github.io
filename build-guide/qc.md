[computer]:Parts.yaml#computer
[USB-C data cable]:Parts.yaml#usb_c
# Check the device (QC)

{{BOM}}

> **Status: not usable on a device yet.** The QC tool (on the
> [`dwarph-qc`](https://github.com/DWARPHs/DWARPH-firmware/tree/dwarph-qc/tools/dwarph_qc) branch of
> DWARPH-firmware) is written and tested against a simulated device, but the firmware side (the
> commands the tool sends to the device) is not written yet. Until it is, check a new device by hand
> with the list below, and run a [short first experiment](../manual.html#first-experiment).

DWARPH-QC will be a guided check of every part of the device, done over the USB cable, with no
network. A new device will run only once it has passed it.

## Run the check {pagestep}

With the device on the [USB-C data cable]{Qty: 1, Cat: tool} and the
[computer]{Qty: 1, Cat: tool}:

```bash
git checkout dwarph-qc                 # in DWARPH-firmware: the tool is on this branch
pip install pyserial pillow numpy
python tools/dwarph_qc/dwarph_qc.py    # or try it without a device: tools/dwarph_qc/fake_device.py
```

It goes through ten steps and asks you to confirm what you see: the device's name on the
display; the coin cell, SD card, cables, antenna, ring and label; the clock; the SD card's
speed; the temperature sensors; the heater; the red, blue and white lights ramping up; the
schedule; a test picture under the capture light; the Wi-Fi.

## Mark it as QC'd {pagestep}

If every step passed, answer **yes** to "Mark this device as QC'd?". The device stores the
result and restarts into normal operation. Keep the report (`qc_reports/`) with the device's
records.

See `tools/dwarph_qc/README.md` on that branch for the protocol and the simulator.
