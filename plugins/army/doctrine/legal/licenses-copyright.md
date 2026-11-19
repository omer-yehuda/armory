# Licenses & copyright

Goal: the project has the right to use everything it contains, and it meets every attribution and license obligation.

## 1. Open-source dependencies
- Inventory the licenses from package metadata: the `license` fields in `package.json` files under `node_modules/` (Grep works well), or Python package metadata (`*.dist-info/METADATA`). You have no shell; if a full automated inventory is needed, ask HQ under HANDBACK to have engineering run `npx license-checker --summary --production` or `pip-licenses`.
- Classify them:
  - **Permissive** (MIT, BSD, ISC, Apache-2.0): usually fine. Keep the copyright notices. Apache-2.0 also requires keeping the NOTICE file and includes patent terms.
  - **Weak copyleft** (LGPL, MPL-2.0, EPL): usually fine to use as a library. Modifications to those files must be shared, and LGPL static linking needs care.
  - **Strong copyleft** (GPL-2.0/3.0): distributing a combined work can require releasing your source under the GPL. This is high risk for proprietary apps that ship code (mobile apps, desktop, npm packages).
  - **Network copyleft** (AGPL-3.0): also triggered by offering the software over a network (SaaS). High risk.
  - **Source-available, not open source** (BUSL, SSPL, Elastic, Commons Clause, "non-commercial"): check the restrictions on commercial use.
  - **No license / unknown:** this means all rights reserved. You may not use it. Flag it HIGH.
- Check that the project's own license (if any) is compatible with its dependencies.

## 2. Copied code
Look for code copied from Stack Overflow (CC BY-SA, which requires attribution), blog posts, tutorials or other repositories. Signals: style shifts, comments with URLs, author names, unusual headers.

## 3. Assets
- **Images, illustrations, icons, video, audio:** where do they come from, and what does their license say? Check stock site licenses (Unsplash/Pexels have their own licenses; Getty/Shutterstock require a paid license per use). Creative Commons: BY = attribution required, SA = share-alike, NC = no commercial use, ND = no modifications.
- **Fonts:** licensed for web embedding or app bundling? (SIL OFL is generally fine. Commercial fonts often restrict web and app use.)
- **Third-party brand logos:** use only per their brand guidelines, and only for factual reference (pass the question to trademarks).
- **Text content:** scraped or copied articles, lyrics, book quotes, or competitor copy are infringement risks.
- **Data sets:** check the license and terms of every data source.

## 4. AI-generated content and code
- Check the terms of the AI tool used (who owns the output, and commercial use rights).
- In many jurisdictions, purely AI-generated works may not be protected by copyright. Note it if the business relies on exclusivity.
- Watch for output that reproduces recognizable copyrighted works or characters.

## Output
A table: item · source · license/terms · obligation · risk (BLOCKER/HIGH/MEDIUM/LOW) · fix (replace, attribute, buy a license, remove). Draft a THIRD_PARTY_NOTICES file if attribution is needed.
