# Generic public site search

Hermes UI exposes a read-only generic search adapter at:

```text
GET /api/site-search?siteUrl=https://example.com&query=star%20wars
```

The endpoint opens a public `http` or `https` page with Playwright, finds a
visible search field, submits the query, reads visible result links, normalizes
the result text, scores matches, and returns JSON.

The Dashboard exposes the same flow in the `Nettsidesøk` section. It sends the
same query parameters to the API, shows structured errors, and renders matching
links with score and snippet.

## Response shape

```json
{
  "sourceUrl": "https://example.com",
  "query": "star wars",
  "normalizedQuery": "star wars",
  "results": [
    {
      "title": "Star.Wars.1977",
      "url": "https://example.com/result",
      "snippet": "Star.Wars.1977 movie",
      "rawText": "Star.Wars.1977 movie",
      "score": 80
    }
  ]
}
```

## Safety boundaries

- Only `http` and `https` URLs are accepted.
- Localhost, `.local`, loopback, private, link-local, and reserved IP targets are
  rejected before browser navigation.
- The adapter only reads visible links and metadata from public pages.
- It does not log in, use user cookies, bypass paywalls, solve CAPTCHA, follow
  magnet links, or download files.
- Magnet links, torrent/download paths, JavaScript URLs, and non-HTTP result
  URLs are filtered out of the returned result list.
- If no visible search field is found, the endpoint returns a structured error.
- Browser launch, navigation, query submission, and result extraction failures
  are returned as structured errors instead of raw tracebacks.

## Restricted metadata mode

Some public sites are classified as high-risk torrent index surfaces. For these
domains, including `1337x.to`, the endpoint still uses the same generic public
search flow but returns an explicit `safety.restrictedMetadataMode=true` marker.

Restricted metadata mode allows:

- opening the public page
- submitting a visible search field
- reading visible result metadata

Restricted metadata mode blocks:

- login or private cookies
- CAPTCHA/paywall bypass
- magnet links
- torrent file extraction
- file downloads

If the site blocks automation, returns a 403-style page, or hides its search
field, the endpoint returns a structured error instead of trying workarounds.

## Scoring

Results are sorted by score and capped at 20 items.

```text
100: exact normalized match
80: flexible separator match
60: all query terms are present
40: at least one query term is present
0: no match, omitted from response
```

Normalization treats spaces, dots, underscores, and dashes as equivalent. For
example, `star wars` can match `star.wars`, `star_wars`, `star-wars`, and
`Star.Wars.1977`.
