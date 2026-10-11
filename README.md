# Tablescape

**Describe your event once. Get a matching, priced dinner kit, made on demand.**

Live demo: **https://arcade-hackathon-m3u9rkxsve9yaqjriftvdg.streamlit.app**

## What it does

Planning a table usually means hunting for napkins, tablecloths and towels that
almost match. Tablescape starts from a theme instead.

1. You describe your event ("blush peonies and eucalyptus, ivory background") and enter a guest count.
2. The app generates **one custom pattern**.
3. That same pattern is applied to **napkins, a tablecloth and tea towels**, so everything matches.
4. Quantities are worked out from your guest count and table count.
5. You see each product with its image and price, an estimated total, and a single checkout link.

Products are made on demand and drop-shipped by Arcade's manufacturer network.

## How it uses the Arcade API

| Step | Endpoint | Purpose |
|---|---|---|
| 1 | `patterns/create`, `jobs/get`, `patterns/get` | Generate the pattern from the theme and poll until it is ready |
| 2 | `categories/list`, `categories/get` | Find each product category by name and get a manufacturable set of options |
| 3 | `products/create`, `jobs/get`, `products/get` | Put the same pattern on each product (with a `fit` crop for non-square sizes) and read back the image and unit price |
| 4 | `checkouts/create` | Create one checkout containing every product (`dropShip: true`) |

Notes on the implementation:

- The pattern is created once and reused, which is what makes the kit match.
- Products are created in parallel (two at a time).
- Requests that hit a rate limit (HTTP 429) wait and retry automatically.
- A product that fails is skipped and reported, and the rest of the kit still goes through.

## Run it locally

```bash
git clone https://github.com/RShruthiCS/arcade-hackathon.git
cd arcade-hackathon
pip install -r requirements.txt

export ARCADE_API_KEY="your-key-here"   # create one in Arcade Studio: Settings > API keys
python3 -m streamlit run app.py
```

Never commit your key. `.env.example` only shows the variable name.

## Project layout

```
app.py             Streamlit interface
kit_builder.py     Kit logic: pattern, products, quantities, checkout
arcade_client.py   Small HTTP helper with job polling and rate-limit retries
examples/          Early experiments used to learn the API
.streamlit/        Theme settings
```

## Known limitations

- The total shown in the app is an **estimate**. Volume discounts, shipping and tax are applied at checkout, so the final price differs.
- **Table runners and placemats** are not included yet. Their non-square sizes were rejected by the API with a "crop must match the selected product size ratio" error that I have not resolved.
- The demo shares one API key, so many simultaneous users may hit rate limits.
- Generation takes roughly one to two minutes.

## What's next

- Table runners and placemats once the crop ratio rule is understood
- An event-type selector (wedding, birthday, baby shower) that adjusts the style
- Optional items such as an upgraded tablecloth, and an adjustable table size
- Showing the final checkout total inside the app

Built for the Arcade hackathon.