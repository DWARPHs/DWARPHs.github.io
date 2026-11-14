[computer]:Parts.yaml#computer
[USB-C data cable]:Parts.yaml#usb_c
# Flash the firmware

{{BOM}}

## Set up the tools {pagestep}

On a [computer]{Qty: 1, Cat: tool}, install ESP-IDF (see the
[Espressif getting-started guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/index.html))
and clone [DWARPH-firmware](https://github.com/DWARPHs/DWARPH-firmware).

## Build and flash {pagestep}

Connect the device with a [USB-C data cable]{Qty: 1, Cat: tool} and run, in the firmware folder:

```bash
idf.py build
idf.py erase-flash flash
```

`erase-flash` clears the device's memory, so a rebuilt device always starts as **not QC'd**.

## Check it starts {pagestep}

The display shows **NOT QC'D** in large letters and the lights flash dimly red, blue, white.
The heater stays off. The device now waits to be checked.
