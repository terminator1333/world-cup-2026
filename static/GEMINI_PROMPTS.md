# 🎨 Gemini prompts for your background images (stills)

Generate **still images** with Gemini (Imagen / "Nano Banana"). Save them into
`static/cities/` and `static/legends/` using the exact filenames in `ASSETS_GUIDE.md`
(e.g. `mexico-city.jpg`, `messi.png`). They become the card backgrounds / legend
figures automatically — replacing the plain dark background.

### Shared style (paste at the start of every prompt)
> Vibrant, modern FIFA-videogame poster aesthetic. Cinematic dramatic lighting, rich
> saturated colors, high detail, crisp and clean. No on-screen text, no watermarks,
> no logos.

### Specs
- **Cities:** 16:9 landscape, high-res (≥1600×900). Keep the composition a touch darker
  toward the bottom so white card text stays readable on top. Save as `.jpg` (or `.png`).
- **Legends:** square or portrait, **transparent background** (`.png`), the figure centered.

---

## 🏙️ City background images → `static/cities/`
Self-contained — paste a whole line, generate at 16:9, save as the filename shown.
Style prefix (already included in each): *Painterly FIFA-style watercolor sports poster,
vibrant saturated colors, dramatic golden-hour light, loose energetic brushstroke texture,
cinematic 16:9, lower third fading into deep shadow for text overlay, no text or logos.*

- **mexico-city.jpg** — "…Scene: Mexico City at golden hour — the golden Ángel de la Independencia monument gleaming in the foreground, dense cityscape beyond, the snow-capped Popocatépetl volcano on the horizon, festive green-white-red energy."
- **new-york-nj.jpg** — "…Scene: the New York City skyline at dusk seen across the Hudson River from New Jersey — the Statue of Liberty in the foreground, the Empire State Building and glittering Manhattan towers glowing against a fiery sunset."
- **dallas.jpg** — "…Scene: the Dallas, Texas skyline at sunset — the illuminated green sphere of Reunion Tower prominent, sleek glass skyscrapers, a sweeping orange-to-violet Texan sky."
- **kansas-city.jpg** — "…Scene: Kansas City at blue hour — its famous grand illuminated fountains spraying in the foreground, a warm-lit downtown skyline behind, soft reflections on the water."
- **houston.jpg** — "…Scene: downtown Houston, Texas at twilight — mirrored glass skyscrapers reflecting a purple sky, sleek modern 'Space City' mood, a faint rocket-launch glow on the horizon."
- **atlanta.jpg** — "…Scene: the Atlanta, Georgia skyline at dusk — the Bank of America Plaza's golden spire towering above a lush green tree canopy, a glowing Ferris wheel, warm Southern sunset."
- **los-angeles.jpg** — "…Scene: Los Angeles at sunset — tall palm-tree silhouettes in the foreground, the downtown LA skyline and Hollywood Hills beyond, a vivid pink-and-orange California sky."
- **seattle.jpg** — "…Scene: Seattle at golden hour — the Space Needle rising over the skyline, the enormous snow-capped Mount Rainier looming behind, Puget Sound waters shimmering in front."
- **philadelphia.jpg** — "…Scene: Philadelphia at golden hour — the ornate City Hall tower amid a modern skyline, warm historic light, proud civic atmosphere."
- **san-francisco.jpg** — "…Scene: San Francisco — the iconic red Golden Gate Bridge emerging from rolling fog in the foreground, the hilly city skyline behind under dramatic late-afternoon light."
- **miami.jpg** — "…Scene: Miami Beach at night — glowing neon art-deco facades, leaning palm trees, turquoise ocean and a moonlit horizon, electric pink-and-cyan tropical colors."
- **boston.jpg** — "…Scene: Boston at dusk — the downtown skyline along the harbor, the cable-stayed Zakim Bridge, calm water reflecting warm city lights."
- **vancouver.jpg** — "…Scene: Vancouver, Canada at golden hour — a glass downtown skyline where towering snow-capped coastal mountains meet the calm Pacific ocean, floatplanes and sailboats, crisp clean light."
- **monterrey.jpg** — "…Scene: Monterrey, Mexico at golden hour — the dramatic jagged Cerro de la Silla mountain dominating the horizon, a modern industrial skyline below, warm desert light."
- **guadalajara.jpg** — "…Scene: Guadalajara, Mexico at golden hour — the twin-spired Guadalajara Cathedral, rolling blue-agave fields on the outskirts, festive mariachi warmth, glowing sunset."
- **toronto.jpg** — "…Scene: Toronto, Canada at blue hour — the towering CN Tower lit in color beside the downtown skyline, calm Lake Ontario reflecting the lights in the foreground."

---

## ⭐ Legend figure images → `static/legends/`

> **Keep them stylized & original.** These describe *non-photorealistic, original
> "legend archetype" figures* evoked by era, nation colors, shirt number and an iconic
> pose — **not** real people's faces. Image tools often refuse real named athletes, and
> this keeps you clear of likeness/trademark issues. Use **plain kit colors with no
> crests, badges, sponsors or names.**

Yearbook-style portraits, painterly like the cities. Generate portrait/square, save as
`.png`. 🏆 = holding the World Cup trophy (only the ones who actually won it).
Style prefix (already in each): *Painterly FIFA-style watercolor portrait, vibrant
saturated colors, warm golden studio light, loose energetic brushstrokes, half-body
yearbook-style pose looking at the viewer, transparent background, no text or logos,
stylized non-photorealistic original character.*

- **pele.png** 🏆 — "…Subject: a legendary Brazilian forward archetype, 1960s era, iconic yellow shirt with green trim and number 10, joyful grin, proudly holding up the golden World Cup trophy."
- **maradona.png** 🏆 — "…Subject: a legendary Argentine number 10 playmaker archetype, 1980s era, sky-blue-and-white striped shirt, dark curly hair, triumphant smile, holding the golden World Cup trophy aloft."
- **beckenbauer.png** 🏆 — "…Subject: an elegant German captain archetype, 1970s era, white shirt number 5, composed confident smile, cradling the golden World Cup trophy."
- **cruyff.png** — "…Subject: a slim visionary Dutch forward archetype, 1970s era, bright orange shirt number 14, cool self-assured smile, arms crossed with a football under one arm."
- **zidane.png** 🏆 — "…Subject: a graceful French maestro archetype, late-1990s era, royal-blue shirt number 10, shaved head, calm proud smile, holding the golden World Cup trophy."
- **ronaldo.png** 🏆 — "…Subject: an explosive Brazilian striker archetype, early-2000s era, yellow shirt number 9, big beaming smile, holding the golden World Cup trophy."
- **maldini.png** — "…Subject: a composed Italian defender archetype, 1990s era, azure-blue shirt number 3, elegant proud half-smile, a football held in one hand."
- **klose.png** 🏆 — "…Subject: a German striker archetype, 2014 era, white shirt number 11, humble friendly grin, holding the golden World Cup trophy."
- **fontaine.png** — "…(use a warm sepia-tinged vintage palette) Subject: a cheerful vintage French striker archetype, 1950s era, dark-blue collared retro shirt number 17, classic old-school smile, a vintage brown leather football under one arm."
- **messi.png** 🏆 — "…Subject: a modern Argentine genius archetype, present day, sky-blue-and-white striped shirt number 10, short dark beard, warm humble smile, holding the golden World Cup trophy."
