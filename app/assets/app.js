const topics = document.querySelector('#topics');
const content = document.querySelector('#content');
const title = document.querySelector('#results-title');
const summary = document.querySelector('#summary');
let graph;

const clean = value => String(value ?? '').replaceAll('_', ' ');
const countLabel = (count, label) => `${count} ${label}${count === 1 ? '' : 's'}`;
const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
const record = (collection, id) => graph[collection].find(item => item.id === id);
const safeSourceUrl = value => {
  try {
    const url = new URL(String(value));
    const hosts = ['gov.uk', 'fca.org.uk', 'bankofengland.co.uk', 'legislation.gov.uk', 'parliament.uk'];
    const trustedHost = hosts.some(host => url.hostname === host || url.hostname.endsWith(`.${host}`));
    return url.protocol === 'https:' && trustedHost ? url.href : null;
  } catch (_) { return null; }
};
const evidenceLabel = evidence => {
  const document = record('documents', evidence.document_id);
  return document && document.synthetic ? '<strong class="meta">Synthetic fixture excerpt</strong>' : '<strong class="meta">Source excerpt</strong>';
};
const sourceLink = (source, label) => {
  const url = safeSourceUrl(source.url);
  return url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}<span class="sr-only"> (opens in a new tab)</span></a>` : '<span class="meta">Source link unavailable: URL did not pass safety checks.</span>';
};

function renderTopic(topic, button) {
  document.querySelectorAll('.topic').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  const sources = topic.source_ids.map(id => record('sources', id)).filter(Boolean);
  const relationships = graph.relationships.filter(item => item.topics.includes(topic.name));
  const events = topic.event_ids.map(id => record('events', id)).filter(Boolean);
  const entities = topic.entity_ids.map(id => record('entities', id)).filter(Boolean);
  const hasClaims = graph.claims.some(item => item.topics.includes(topic.name));
  title.textContent = topic.name;
  summary.textContent = [countLabel(sources.length, 'source'), countLabel(events.length, 'event'), countLabel(relationships.length, 'relationship')].join(' · ');
  const url = new URL(window.location.href); url.searchParams.set('topic', topic.name); history.replaceState({}, '', url);
  const relationshipCards = relationships.map(edge => {
    const from = record('entities', edge.source_entity_id);
    const to = record('entities', edge.target_entity_id);
    const source = record('sources', edge.source_id);
    return `<article class="card" id="${escapeHtml(edge.id)}"><span class="status">Document status as of ${escapeHtml(source.status_as_of)}: ${escapeHtml(clean(source.status))}</span><h4>${escapeHtml(from.name)} → ${escapeHtml(to.name)}</h4><p class="meta">Relationship: ${escapeHtml(clean(edge.kind))}</p><blockquote class="evidence">${evidenceLabel(edge.evidence)}<br>“${escapeHtml(edge.evidence.quote)}”<br><small>Evidence locator: ${escapeHtml(edge.evidence.section)}</small></blockquote>${sourceLink(source, `View primary source: ${source.title}`)}</article>`;
  }).join('');
  const entityCards = entities.map(item => {
    const count = relationships.filter(edge => item.id === edge.source_entity_id || item.id === edge.target_entity_id).length;
    return `<article class="card"><p class="meta">${escapeHtml(clean(item.kind))}</p><h4>${escapeHtml(item.name)}</h4><p>${count} relationship${count === 1 ? '' : 's'} in this topic.</p></article>`;
  }).join('');
  const eventCards = events.map(item => {
    const source = record('sources', item.source_id);
    return `<article class="card"><span class="status">Document status as of ${escapeHtml(item.status_as_of)}: ${escapeHtml(clean(item.status))}</span><h4>${escapeHtml(clean(item.title))}</h4><p class="meta">${escapeHtml(item.date || 'Date not asserted in sample')}</p><blockquote class="evidence">${evidenceLabel(item.evidence)}<br>“${escapeHtml(item.evidence.quote)}”<br><small>Evidence locator: ${escapeHtml(item.evidence.section)}</small></blockquote>${sourceLink(source, 'Inspect event source')}</article>`;
  }).join('');
  const sourceCards = sources.map(item => `<article class="card"><span class="status">Document status as of ${escapeHtml(item.status_as_of)}: ${escapeHtml(clean(item.status))}</span><h4>${escapeHtml(item.title)}</h4><p class="meta">${escapeHtml(item.publisher)} · ${escapeHtml(item.published_on || 'Publication date unavailable')}</p>${sourceLink(item, 'Open primary source')}</article>`).join('');
  const coverageNote = sources.length && !hasClaims ? '<p class="coverage-note">Primary sources are registered for this topic, but the synthetic sample has no extracted claims yet. Inspect the <a href="#sources-view">source links below</a> to explore this gap in the demo’s coverage.</p>' : '';
  content.innerHTML = `<nav class="view-links" aria-label="Topic result sections"><a href="#entities-view">Entities</a><a href="#events-view">Events</a><a href="#relationships-view">Relationships and evidence</a><a href="#sources-view">Sources</a></nav>${coverageNote}${section('entities-view', 'Entities', entityCards, 'No entities are represented for this topic in the bounded sample.')}${section('events-view', 'Events', eventCards, 'No events are represented for this topic in the bounded sample.')}${section('relationships-view', 'Relationships and evidence', relationshipCards, 'No relationships are represented for this topic in the bounded sample.')}${section('sources-view', 'Primary sources', sourceCards, 'No sources are represented for this topic in the bounded sample.')}`;
  document.querySelector('#results').focus();
}

function section(id, heading, cards, emptyMessage) {
  return `<section id="${id}" class="result-group"><h3>${heading}</h3>${cards ? `<div class="grid">${cards}</div>` : `<p class="empty">${emptyMessage} This does not mean there has been no policy activity.</p>`}</section>`;
}

function topicsFromGraph(graphData) {
  const names = new Set();
  ['sources', 'claims', 'events', 'relationships'].forEach(collection => {
    graphData[collection].forEach(item => item.topics.forEach(name => names.add(name)));
  });
  return [...names].sort((left, right) => left.localeCompare(right)).map(name => {
    const relationships = graphData.relationships.filter(item => item.topics.includes(name));
    return {
      name,
      source_ids: [...new Set(graphData.sources.filter(item => item.topics.includes(name)).map(item => item.id))].sort(),
      entity_ids: [...new Set(relationships.flatMap(item => [item.source_entity_id, item.target_entity_id]))].sort(),
      event_ids: [...new Set(graphData.events.filter(item => item.topics.includes(name)).map(item => item.id))].sort()
    };
  });
}

async function loadData() {
  const staticMode = document.querySelector('meta[name="policygraph-data-mode"]')?.content === 'static';
  if (!staticMode) {
    try {
      const [topicResponse, graphResponse] = await Promise.all([fetch('/api/topics'), fetch('/api/graph')]);
      if (!topicResponse.ok || !graphResponse.ok) throw new Error('API unavailable');
      return {topicData: await topicResponse.json(), graphData: await graphResponse.json(), staticMode: false};
    } catch (_) {
      // A static fallback keeps local file-server previews usable without an API.
    }
  }
  const graphResponse = await fetch('data/graph.json');
  if (!graphResponse.ok) throw new Error('Static graph unavailable');
  const graphData = await graphResponse.json();
  return {topicData: topicsFromGraph(graphData), graphData, staticMode: true};
}

async function start() {
  try {
    const {topicData, graphData, staticMode} = await loadData();
    graph = graphData;
    if (staticMode) {
      const documentation = document.querySelector('#documentation-link');
      documentation.href = 'https://github.com/mindblastsg/policygraph-uk-digital-finance#start-here';
      documentation.textContent = 'Project documentation';
    }
    if (!topicData.length) { topics.innerHTML = '<p class="empty">No topics are covered by the current sample.</p>'; return; }
    topics.innerHTML = '';
    const requested = new URL(window.location.href).searchParams.get('topic'); let selected;
    topicData.forEach(topic => { const button = document.createElement('button'); button.className = 'topic'; button.type = 'button'; button.setAttribute('aria-pressed','false'); button.textContent = topic.name; button.addEventListener('click', () => { try { renderTopic(topic, button); } catch (_) { content.innerHTML = '<p class="error" role="alert">This topic could not be displayed safely.</p>'; } }); topics.append(button); if (topic.name === requested) selected = button; });
    (selected || topics.querySelector('.topic')).click();
  } catch (_) {
    topics.innerHTML = '<p class="error" role="alert">The sample graph could not be loaded. Try refreshing, or check the deployment status.</p>';
  }
}
start();
