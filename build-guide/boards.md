[mainboard]:Parts.yaml#mainboard
[heater/sensor board]:Parts.yaml#heater_board
[LED board]:Parts.yaml#led_board
[12 V distribution board]:Parts.yaml#distribution_board
[12 V power supply]:Parts.yaml#psu_12v
# Get the circuit boards

{{BOM}}

DWARPH uses three boards per device, plus one 12 V distribution board shared by several
devices. All four are designed in EasyEDA Pro; the files are in DWARPH-hardware.

## Order them assembled {pagestep}

For each board, upload its Gerber zip, BOM and pick-and-place files from
`PCBs/fabrication/<board>/` to a PCB assembly service:

* one [mainboard]{Qty: 1, Cat: board}
* one [heater/sensor board]{Qty: 1, Cat: board}
* one [LED board]{Qty: 1, Cat: board}
* one [12 V distribution board]{Qty: 1, Cat: board} and one [12 V power supply]{Qty: 1}, shared by up to 10 devices

Schematics, layouts (PDF) and 3D models (STEP) of each board are in `PCBs/docs/<board>/`.

## Check them {pagestep}

Check every board for missing or misaligned parts and solder bridges before going further.

> **TODO:** photos of each assembled board, and a short electrical check (e.g. no short
> between 12 V and ground on the mainboard).
