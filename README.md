# winnowed-site

Marketing site for [Winnowed](https://winnowed.app) — the subscription tracker designed around a quarterly review ritual.

## Structure

```
winnowed-site/
├── index.html              → winnowed.app/
├── styles.css              → shared stylesheet
├── privacy/index.html      → winnowed.app/privacy
├── support/index.html      → winnowed.app/support
└── images/
    ├── stack.png
    ├── review.png
    └── widget.png
```

Single-page HTML/CSS with no build step. Typography is Fraunces (display) and Inter (body) via Google Fonts. Colors pull from Winnowed's 5-stage harvest palette (sage → burgundy).

## Deploy (Cloudflare Pages)

Same pattern as the Minuted site:

1. Create a new GitHub repo named `winnowed-site` under `09kleinkd`.
2. `git init`, `git add .`, `git commit`, `git push`.
3. In Cloudflare, Workers & Pages → Create → Pages → Connect to Git → pick `winnowed-site`.
4. Build settings: leave everything blank. Output directory: `/`.
5. Deploy.
6. Custom domain: add `winnowed.app` and `www.winnowed.app`.

Every `git push` to `main` auto-deploys.

## Analytics

[Plausible](https://plausible.io) — privacy-preserving, no cookies, no personal data. Domain is set to `winnowed.app` in the script tag on each page.
