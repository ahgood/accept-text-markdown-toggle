# Privacy Policy

**Extension:** Accept: text/markdown Toggle
**Last updated:** 28 August 2026

## Summary

This extension does not collect, store, transmit, or sell any user data. There is no
analytics, no tracking, no telemetry, and no server component. Nothing leaves your
browser.

## What the extension does

When you click its toolbar button, the extension sets the `Accept` request header of the
current tab's top-level page request to `text/markdown` and reloads the page. Clicking
again removes that change, so the tab returns to Chrome's default `Accept` header.

## What it accesses, and why

- **The current tab's id**, to scope the header change to the one tab you clicked in, so
  other tabs are unaffected.
- **The current tab's URL scheme**, read only to confirm the page is `http` or `https`
  before acting. The URL is not stored, logged, or transmitted.

The extension does not read page content, cookies, browsing history, form input,
passwords, or any personal information. It has no content scripts and never injects code
into web pages.

## What it stores

The on/off state of each tab is held as a Chrome `declarativeNetRequest` session rule,
which lives in browser memory only. It is discarded when Chrome closes. The extension
uses no `chrome.storage`, no cookies, no local storage, and no remote database.

## What it transmits

Nothing. The extension makes no network requests of its own and communicates with no
server, including any operated by the developer. The only network effect it has is
changing one header on requests your browser was already making to sites you chose to
visit.

## Permissions

- **`declarativeNetRequestWithHostAccess`** is required because modifying a request
  header is only possible through Chrome's `declarativeNetRequest` API. This is the
  narrower of the two available variants, permitting header modification only on sites
  you have granted access to.
- **`<all_urls>`** is required because Markdown content negotiation is a site-by-site
  convention that any website may adopt, so the extension cannot know in advance which
  sites you will use it on. It is used solely to apply the header rule to the tab you
  explicitly click the button on. You can narrow this at any time from
  `chrome://extensions` (Details > Site access), and the extension will continue to work
  on the sites you allow.

## Third parties

There are none. No data is shared with, sold to, or transferred to any third party, and
no third-party libraries or remote code are used. All code is contained in the extension
package and is available to read at
<https://github.com/ahgood/accept-text-markdown-toggle>.

## Changes to this policy

Any change to this policy will be published in this file, with the date above updated.
The revision history is public in the repository's commit log.

## Contact

Questions about this policy can be raised at
<https://github.com/ahgood/accept-text-markdown-toggle/issues>.
