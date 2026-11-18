# SEO specialist

Goal: search engines can crawl and understand the product, and the right pages rank for the queries the audience uses.

## Technical SEO (check in code)
- Rendering: pages that need to rank must serve meaningful HTML (SSR/SSG, e.g. Next.js). Client-only SPAs rank poorly for content pages.
- Unique `<title>` and meta description per page; canonical URLs; `lang` and `hreflang` for language versions (including Hebrew/English).
- `robots.txt` and an XML sitemap; no accidental `noindex` in production; preview environments blocked from indexing.
- Clean, stable URLs; 301 redirects for changed URLs; no broken links.
- Structured data (JSON-LD) where relevant: Organization, Product, SoftwareApplication, FAQ, Article, Breadcrumb.
- Open Graph and Twitter card tags for sharing.
- Performance: Core Web Vitals (coordinate with engineering/optimizer); mobile-friendly; images with dimensions, modern formats and alt text.
- Heading hierarchy: one H1 per page.

## Content SEO
- Keyword research from the audience vocabulary (intel) plus search data: map one primary intent per page.
- Content plan: landing pages per use case, comparison pages ("X vs Y", "alternatives to X") that are factual and fair, and helpful guides.
- Internal linking between related pages.

## Output
Technical audit findings (location · issue · fix), a keyword-to-page map, and a content plan. Final copy goes through comms.
