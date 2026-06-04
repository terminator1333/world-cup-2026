# 🎨 Animated assets — drop-in guide

Generate your own images/animations and drop them in the folders below using the
**exact filenames**. The app auto-detects them on the next refresh — no code changes.

- **Still image** (`.jpg`, `.png`) → recommended. For cities use `.jpg`; for legend
  figures use a transparent `.png`.
- **Animated image / video** (`.gif`, `.webp`, `.apng`, `.webm`, `.mp4`) → also supported
  if you ever want motion.

If two formats exist for one slug, the order of preference is:
`.webm → .mp4 → .gif → .webp → .apng → .png → .jpg`
(so if you only drop in a `.jpg`/`.png`, that's what gets used).

## 🏙️ City backgrounds → `static/cities/`
Recommended: landscape, ~1200×675, looping, subtle motion (skyline, lights, crowd).

| City | Filename (any supported ext) |
|------|------------------------------|
| Mexico City | `mexico-city.webm` |
| New York / NJ | `new-york-nj.webm` |
| Dallas | `dallas.webm` |
| Kansas City | `kansas-city.webm` |
| Houston | `houston.webm` |
| Atlanta | `atlanta.webm` |
| Los Angeles | `los-angeles.webm` |
| Seattle | `seattle.webm` |
| Philadelphia | `philadelphia.webm` |
| San Francisco | `san-francisco.webm` |
| Miami | `miami.webm` |
| Boston | `boston.webm` |
| Vancouver | `vancouver.webm` |
| Monterrey | `monterrey.webm` |
| Guadalajara | `guadalajara.webm` |
| Toronto | `toronto.webm` |

## ⭐ Legend figures → `static/legends/`
Recommended: square or portrait, ~500×500, transparent background if possible,
short looping animation (idle/celebration).

| Legend | Filename (any supported ext) |
|--------|------------------------------|
| Pelé | `pele.webm` |
| Diego Maradona | `maradona.webm` |
| Franz Beckenbauer | `beckenbauer.webm` |
| Johan Cruyff | `cruyff.webm` |
| Zinedine Zidane | `zidane.webm` |
| Ronaldo Nazário | `ronaldo.webm` |
| Paolo Maldini | `maldini.webm` |
| Miroslav Klose | `klose.webm` |
| Just Fontaine | `fontaine.webm` |
| Lionel Messi | `messi.webm` |

## 🖼️ Whole-page backdrop → `static/`
`background.jpg` (or `.png`/`.gif`/`.webp`) — a full-screen image shown faintly behind
**every page**. If you don't add one, the app automatically uses your first city image
from `static/cities/` as the backdrop. Animated `.gif`/`.webp` animate for free.

## 🏆 Optional hero background → `static/`
`hero.webm` (or `.mp4`/`.gif`/`.jpg`) — a wide image/animation behind the page title.

> Tip: keep each file lean (videos < ~3–5 MB) so the page loads fast, especially
> on phones. These files are committed to the repo and deployed to Streamlit Cloud.
