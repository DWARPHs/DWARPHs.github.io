[mainboard]:Parts.yaml#mainboard
[CR1220 coin cell]:Parts.yaml#cr1220
[multimeter]:Parts.yaml#multimeter
# Fit the clock battery

{{BOM}}

The real-time clock (DS3231M) on the mainboard keeps the time when the device has no power.
Without its cell, a device that loses power restarts with no valid time: it then waits, with
its heater and lights off, until it can get the time from the network.

## Fit the cell {pagestep}

Push a [CR1220 coin cell]{Qty: 1} into the holder on the [mainboard],
**+ side up**, until it clicks.

## Check it {pagestep}

With a [multimeter]{Qty: 1, Cat: tool}, check about 3 V across the holder.

> **TODO:** photo of the holder with the cell in place.
