[heater/sensor board]:Parts.yaml#heater_board
[conformal coating]:Parts.yaml#conformal_coating
[isopropyl alcohol]:Parts.yaml#ipa
[polyimide masking tape]:Parts.yaml#masking_tape
[brush]:Parts.yaml#coating_brush
[nitrile gloves]:Parts.yaml#gloves
[UV torch]:Parts.yaml#uv_torch
[multimeter]:Parts.yaml#multimeter
# Coat the heater board

{{BOM}}

> **Important.** The heater / temperature-sensor board sits next to the water for weeks, warm,
> in humid air, with condensation every night when the temperature drops. Uncoated, it
> corrodes: sensors start reading wrong, the heater driver fails, and in the worst case the
> board shorts. **Do not skip this step.**

Coat the board **after** it has been checked (step [Get the circuit boards](boards.md)) and **before** it is wired and
mounted. Once coated, repairs are much harder, so check it first.

Work in a well-ventilated place, away from flames, wearing [nitrile gloves]{Qty: 1, Cat: tool},
and follow the safety data sheet of the coating.

> **TODO:** the coating product DWARPH uses, and a photo or drawing of the
> [heater/sensor board] showing exactly which areas to mask.

## Clean the board {pagestep}

Scrub both sides of the [heater/sensor board] with [isopropyl alcohol]{Qty: 1, Cat: tool} to
remove flux and fingerprints; coating does not stick to dirt or flux. Let it dry completely
(at least 30 minutes, or warm and dry).

## Mask what must stay uncoated {pagestep}

Cover with [polyimide masking tape]{Qty: 1, Cat: tool}:

* the **connectors** (cable sockets and the heater-wire terminals): coating inside a
  connector stops it making contact;
* **mounting holes and screw pads**, if they carry ground or must touch the enclosure;
* **any contact that must touch something**: test points you will need later, or a thermal
  contact between the heater and the vessel.

Press the tape edges down firmly so the coating cannot creep under them.

## Apply the coating {pagestep}

Apply the [conformal coating]{Qty: 1} in **two or three thin coats** rather than one thick one,
with a [brush]{Qty: 1, Cat: tool} or as a spray, following the product's drying time between
coats. Cover every component and solder joint, including the edges and the underside of
components; tilt the board so nothing is shadowed. Coat both sides if both are exposed.

## Cure and inspect {pagestep}

Let it cure fully, as long as the product says (often 24 hours) before handling or powering it.
Then remove the tape slowly. Check under good light, or with a [UV torch]{Qty: 1, Cat: tool} for a
UV-tracer coating: no bare solder joints or pins, no bubbles, no coating inside connectors.
Touch up gaps with the brush and let them cure.

## Check the board again {pagestep}

With a [multimeter]{Qty: 1, Cat: tool}, check that the connector contacts are still clean (no
coating on them) and that there is no short between the heater supply and ground. DWARPH-QC
checks the sensors and the heater after assembly; its physical check also asks whether this
board is coated.
