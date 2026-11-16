[computer]:Parts.yaml#computer
[USB-C data cable]:Parts.yaml#usb_c
# Flash the firmware

{{BOM}}

## Set up the tools {pagestep}

On a [computer]{Qty: 1, Cat: tool}, install **ESP-IDF 5.0 or newer** (see the
[Espressif getting-started guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/index.html))
and clone [DWARPH-firmware](https://github.com/DWARPHs/DWARPH-firmware). On Linux, your user needs
access to the serial port (usually the `dialout` group).

## Build and flash {pagestep}

Connect the device with a [USB-C data cable]{Qty: 1, Cat: tool} and run, in the firmware folder:

```bash
idf.py set-target esp32s3        # once, in a fresh clone
idf.py build
idf.py -p <PORT> erase-flash flash monitor
```

`<PORT>` is the serial port (`/dev/ttyACM0` on Linux, `COM3` or similar on Windows). `erase-flash`
clears the device's memory, so a rebuilt device starts from a clean state; `Ctrl+]` leaves the
monitor.

## Check it starts {pagestep}

The display shows the boot steps, then the device's status. With no schedule on the SD card it
stays idle: heater and lights off, no pictures.

> **Planned with DWARPH-QC:** a device that has not passed QC will show **NOT QC'D** and flash its
> lights dimly until it is checked. That part of the firmware is not written yet (next step).
