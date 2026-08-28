// Per-tab Accept header toggle.
//
// State lives entirely in the declarativeNetRequest *session* rule set: a rule whose id
// equals a tab id means "this tab requests text/markdown". Nothing is cached here, so the
// service worker can be terminated and restarted without the UI going out of sync.
// Session rules also disappear when Chrome quits, so no state carries between browser runs.

const HEADER = "Accept";
const MARKDOWN = "text/markdown";
const BADGE_ON = "MD";

const TITLE_ON = "Accept: text/markdown (click to restore browser default)";
const TITLE_OFF = "Accept: browser default (click to request text/markdown)";

async function isOn(tabId) {
  const rules = await chrome.declarativeNetRequest.getSessionRules();
  return rules.some((rule) => rule.id === tabId);
}

function markdownRule(tabId) {
  return {
    id: tabId,
    priority: 1,
    action: {
      type: "modifyHeaders",
      requestHeaders: [{ header: HEADER, operation: "set", value: MARKDOWN }]
    },
    // tabIds is only honoured on session rules, which is why this is not a dynamic rule.
    condition: { tabIds: [tabId], resourceTypes: ["main_frame"] }
  };
}

async function paint(tabId, on) {
  // Per-tab action state is cleared by Chrome on navigation, so this gets re-run often.
  await chrome.action.setBadgeText({ tabId, text: on ? BADGE_ON : "" });
  await chrome.action.setBadgeBackgroundColor({ tabId, color: "#1a7f37" });
  await chrome.action.setTitle({ tabId, title: on ? TITLE_ON : TITLE_OFF });
}

chrome.action.onClicked.addListener(async (tab) => {
  // Rule ids must be positive integers, which every real tab id is.
  if (!tab || typeof tab.id !== "number" || tab.id <= 0) return;
  const tabId = tab.id;

  // An empty url means we have no host access to this tab. Without a warning here the
  // click just does nothing, with nothing anywhere to explain why.
  if (typeof tab.url !== "string" || tab.url === "") {
    console.warn("No access to this tab's URL. Grant this extension access to the site "
      + "(chrome://extensions > Details > Site access) to toggle here.");
    return;
  }
  if (!/^https?:/.test(tab.url)) {
    console.warn("Cannot modify request headers for", tab.url);
    return;
  }

  try {
    const on = await isOn(tabId);
    await chrome.declarativeNetRequest.updateSessionRules({
      removeRuleIds: [tabId],
      addRules: on ? [] : [markdownRule(tabId)]
    });
    await paint(tabId, !on);
    // Without bypassCache the navigation can be served from cache and the new header
    // never reaches the server.
    await chrome.tabs.reload(tabId, { bypassCache: true });
  } catch (err) {
    console.warn("toggle failed for tab", tabId, err);
  }
});

chrome.tabs.onUpdated.addListener(async (tabId, info) => {
  // Both stages, deliberately: per-tab action state is cleared around navigation, and
  // repainting once the load completes keeps the badge correct whichever order those
  // two happen in.
  if (info.status !== "loading" && info.status !== "complete") return;
  try {
    await paint(tabId, await isOn(tabId));
  } catch (err) {
    // Tab closed mid-navigation; nothing to paint.
  }
});

chrome.tabs.onRemoved.addListener((tabId) => {
  // Tab ids can be recycled; drop the rule so a future tab cannot inherit it.
  chrome.declarativeNetRequest.updateSessionRules({ removeRuleIds: [tabId] })
    .catch(() => {});
});
