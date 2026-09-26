/* 첫 화면 통합 검색. 화면과 따로 도는 작업(Web Worker)에서 검색 목록을 받고 글자를 찾는다.
   색인을 미리 만들지 않아 받은 뒤 곧바로 찾을 수 있다. */
var docs = null;
var loading = null;

function norm(s) { return (s || '').toLowerCase(); }

function load(url) {
  return fetch(url).then(function (r) { return r.json(); }).then(function (d) {
    docs = Object.keys(d).map(function (k) {
      var v = d[k];
      return { doc: v.doc || '', title: v.title || '', url: v.url, content: v.content || '',
               h: norm((v.doc || '') + ' ' + (v.title || '')), c: norm(v.content) };
    });
  });
}

function search(q) {
  var terms = norm(q).split(/\s+/).filter(Boolean);
  if (!terms.length) return { results: [], total: 0 };
  var out = [];
  for (var i = 0; i < docs.length; i++) {
    var d = docs[i], score = 0, ok = true;
    for (var j = 0; j < terms.length; j++) {
      var t = terms[j];
      if (d.h.indexOf(t) >= 0) { score += 10; }
      else if (d.c.indexOf(t) >= 0) { score += 1; }
      else { ok = false; break; }
    }
    if (ok) out.push([score, i]);
  }
  out.sort(function (a, b) { return b[0] - a[0] || a[1] - b[1]; });
  var results = out.slice(0, 50).map(function (p) {
    var d = docs[p[1]];
    var at = d.c.indexOf(terms[0]);
    var start = at > 40 ? at - 40 : 0;
    return { doc: d.doc, title: d.title, url: d.url, snip: d.content.slice(start, start + 160), cut: start > 0 };
  });
  return { results: results, total: out.length };
}

onmessage = function (e) {
  var m = e.data;
  if (!loading) loading = load(m.url);
  loading.then(function () {
    if (m.type === 'load') {
      postMessage({ type: 'ready', count: docs.length });
    } else if (m.type === 'query') {
      var r = search(m.q);
      postMessage({ type: 'results', id: m.id, q: m.q, results: r.results, total: r.total });
    }
  }).catch(function () {
    postMessage({ type: 'error' });
  });
};
