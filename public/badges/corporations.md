# Corporation badge color proposals

Center is the first color; frame is the second. These are design proposals, not official color specifications.
The Distinct palette uses 47 unique pairs, with 12 revised palettes. Original slash alternatives remain available in Original mode.

## Revised palettes

| Corporation | Original center / frame | Distinct center / frame | Design reason |
| --- | --- | --- | --- |
| Arklight | Blue / White | Light blue / Navy | Light blue and navy follow the maritime logo and separate Arklight from Morning Star. |
| Astrodrill | Orange / Dark grey | Steel / Orange | A steel center with an orange frame gives Astrodrill an industrial look. |
| Mining Guild | Orange / Black | Dark orange / Steel | Dark orange suggests mineral ore, with a cool steel frame. |
| Palladin Shipping | Yellow / Black | Dark yellow / Steel | Dark yellow and steel distinguish Palladin from Helion’s yellow and black. |
| Philares | Orange / Black | Dark green / Orange | Green takes the center, using the green in the original alternatives and keeping an orange frame. |
| PhoboLog | Navy / White | White / Navy | A white center and navy frame echo the moon logo and reverse the original pair. |
| Pristar | Orange / Black | Gold / Purple | Gold complements the orange emblem while purple gives Pristar a distinct frame. |
| Saturn Systems | Navy / White | Navy / Gold | Navy keeps the night-sky theme; a gold frame gives Saturn a warm ring. |
| Stormcraft Incorporated | Orange / Black | Black / Bright orange | The orange logo stands against a black center, surrounded by a bright orange frame. |
| Teractor | Orange / Black | Bright orange / Black | Bright orange keeps Teractor’s identity and separates it from Mining Guild’s darker palette. |
| Tycho Magnetics | Yellow / White | Yellow / Blue | A blue frame uses the previously suggested accent and separates Tycho from Pharmacy Union. |
| Vitor | Orange / White | Coral / White | Coral gives Vitor a warmer pink-orange identity while retaining its white frame. |

## All corporation palettes

| Corporation | Distinct center / frame | Original center | Original frame | Optional accent |
| --- | --- | --- | --- | --- |
| Aphrodite | Orange / Yellow | Orange | Yellow | — |
| Arcadian Communities | Black / White | Black | White | — |
| Aridor | Orange / Bronze | Orange | Bronze | — |
| Arklight | Light blue / Navy | Blue | White / Black | Black |
| Astrodrill | Steel / Orange | Orange | Dark grey / Black | Yellow |
| Celestic | Orange / Turquoise | Orange | Turquoise | — |
| Cheung Shing Mars | Red / Black | Red | Black | — |
| Credicor | Purple / White | Purple | White | — |
| Ecoline | Green / Green | Green | Green | White |
| Ecotec | Green / Yellow | Green | Yellow | — |
| Factorum | Orange / Silver | Orange | Silver | — |
| Helion | Yellow / Black | Yellow | Black | Orange |
| Interplanetary Cinematics | Red / Yellow | Red | Yellow | — |
| Inventrix | Light blue / Blue | Light blue | Blue | — |
| Kuiper Cooperative | Light blue / White | Light blue | White | — |
| Lakefront Resorts | Orange / Blue | Orange | Blue | — |
| Manutech | Red / White | Red | White | — |
| Mining Guild | Dark orange / Steel | Orange | Black | Bronze |
| Mons Insurance | Orange / White | Orange | White | Red |
| Morning Star Inc. | Blue / White | Blue | White | Yellow |
| Nirgal Enterprises | White / Orange | White | Orange | — |
| Palladin Shipping | Dark yellow / Steel | Yellow | Black / Dark grey | White |
| Pharmacy Union | Yellow / White | Yellow / Slime | White | Slime |
| Philares | Dark green / Orange | Orange | Black / Green | Green |
| PhoboLog | White / Navy | Navy | White | Turquoise |
| Polyphemos | Black / Red | Black | Red | — |
| Point Luna | Silver / Dark grey | Silver | Dark grey | — |
| Poseidon | Turquoise / Black | Turquoise | Black | — |
| Pristar | Gold / Purple | Orange | Black | Purple |
| Recyclon | Red / Orange | Red | Orange | — |
| Robinson Industries | White / Black | White | Black | — |
| Sagitta | Green / Black | Green | Black | — |
| Saturn Systems | Navy / Gold | Navy | White | Yellow |
| Septem Tribus | Beige / White | Beige | White | — |
| Spire | Black / Dark grey | Black | Dark grey / Silver | — |
| Splice | White / Red | White | Red | — |
| Stormcraft Incorporated | Black / Bright orange | Orange | Black | Light blue |
| Teractor | Bright orange / Black | Orange | Black | Turquoise |
| Terralabs Research | Turquoise / Green | Turquoise | Green | — |
| Tharsis Republic | Orange / Brown | Orange | Brown | — |
| Thorgate | Navy / Red | Navy | Red | — |
| Tycho Magnetics | Yellow / Blue | Yellow | White | Blue |
| United Nations Mars Initiative | Turquoise / White | Turquoise | White | — |
| Utopia Invest | Green / White | Green | White | — |
| Valley Trust | Blue / Dark grey | Blue | Dark grey | — |
| Viron | Black / Beige | Black | Beige | — |
| Vitor | Coral / White | Orange | White | Purple |

## Repeated pairs in the original palettes

The Distinct palette has no repeated center/frame pairs. The following repeats are retained for comparison in Original mode:

- **Blue / White**: Arklight, Morning Star Inc..
- **Navy / White**: PhoboLog, Saturn Systems.
- **Orange / Black**: Astrodrill, Mining Guild, Philares, Pristar, Stormcraft Incorporated, Teractor.
- **Orange / White**: Mons Insurance, Vitor.
- **Yellow / Black**: Helion, Palladin Shipping.
- **Yellow / White**: Pharmacy Union, Tycho Magnetics.

Suggested accents color the outer border, crest, and bottom plate by default. Wings match the frame by default. Independent wing, crest, and outer-border color selectors can override these defaults.
Custom mode provides 30 centers and 30 colors each for frames, wings, crests, and outer borders, using separate aligned layers.
Badge names stay visible in the gallery so color is not the only identifier.

Names normalized against the project include Inventrix, PhoboLog, Terralabs Research, and Tharsis Republic; Gul means yellow. Slime is provisionally #B6D52D.

Edit `scripts/corporation_badges.json`, then run `python3 scripts/render_corporation_badges.py` and the WebP exporter.
