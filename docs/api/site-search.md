# Generic public site search

Hermes UI exposes a read-only generic search adapter at:

```text
GET /api/site-search?siteUrl=https://example.com&query=star%20wars
```

The endpoint opens a public `http` or `https` page with Playwright, finds a
visible search field, submits the query, reads visible result links, normalizes
the result text, scores matches, and returns JSON.

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
- If no visible search field is found, the endpoint returns a structured error.

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
