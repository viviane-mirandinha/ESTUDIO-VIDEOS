// IGProf — full-profile dumper. Inject once per instagram.com tab via javascript_tool.
// State lives on window.__igProf; return values are always slim (no cursors, no raw items).
(() => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const csrf = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '';
  const H = {
    'x-csrftoken': csrf,
    'x-ig-app-id': '936619743392459',
    'x-requested-with': 'XMLHttpRequest',
    'accept': '*/*'
  };
  const S = window.__igProf = window.__igProf || {
    uid: null, username: null, total: 0, followers: 0,
    rows: new Map(),          // pk -> projected row
    feedCursor: null, feedMore: true,
    clipsCursor: null, clipsMore: true
  };

  const project = m => ({
    pk: String(m.pk || m.id).split('_')[0],
    code: m.code,
    taken_at: m.taken_at,
    media_type: m.media_type,
    product_type: m.product_type || '',
    like_count: m.like_and_view_counts_disabled ? null : (m.like_count ?? null),
    comment_count: m.comment_count ?? null,
    plays: m.ig_play_count ?? m.play_count ?? null,
    view_count: m.view_count ?? null,
    likes_hidden: !!m.like_and_view_counts_disabled,
    caption: ((m.caption && m.caption.text) || '').slice(0, 600),
    video_duration: m.video_duration ?? null,
    carousel_count: m.carousel_media_count ?? (m.carousel_media ? m.carousel_media.length : null),
    coauthors: (m.coauthor_producers || []).map(u => u.username),
    location: (m.location && m.location.name) || null
  });

  window.IGProf = {
    async init(username) {
      const r = await fetch(`/api/v1/users/web_profile_info/?username=${encodeURIComponent(username)}`,
        { headers: H, credentials: 'include' });
      if (!r.ok) return { error: r.status };
      const u = (await r.json()).data.user;
      S.uid = u.id; S.username = u.username;
      S.total = u.edge_owner_to_timeline_media.count;
      S.followers = u.edge_followed_by.count;
      return {
        uid: u.id, username: u.username, posts: S.total, followers: S.followers,
        following: u.edge_follow.count, is_private: u.is_private,
        is_verified: u.is_verified, category: u.category_name || null,
        bio: (u.biography || '').slice(0, 300)
      };
    },

    // 4 timeline pages per call (~130 posts), safe under the 45 s JS timeout.
    async feedPage() {
      let status = 200;
      for (let p = 0; p < 4 && S.feedMore; p++) {
        const url = `/api/v1/feed/user/${S.uid}/?count=33` +
                    (S.feedCursor ? `&max_id=${encodeURIComponent(S.feedCursor)}` : '');
        const r = await fetch(url, { headers: H, credentials: 'include' });
        status = r.status;
        if (!r.ok) { S.feedMore = r.status !== 400; break; }
        const d = await r.json();
        for (const it of (d.items || [])) { const row = project(it); S.rows.set(row.pk, row); }
        S.feedMore = !!d.more_available;
        S.feedCursor = d.next_max_id || null;
        if (!S.feedCursor) S.feedMore = false;
        await sleep(350);
      }
      return { collected: S.rows.size, total: S.total, more: S.feedMore, status };
    },

    // Reels tab: authoritative ig_play_count. Merges into existing rows by pk.
    async clipsPage() {
      let merged = 0, status = 200;
      for (let p = 0; p < 6 && S.clipsMore; p++) {
        const body = `target_user_id=${S.uid}&page_size=20` +
                     (S.clipsCursor ? `&max_id=${encodeURIComponent(S.clipsCursor)}` : '');
        const r = await fetch('/api/v1/clips/user/', {
          method: 'POST', credentials: 'include',
          headers: { ...H, 'content-type': 'application/x-www-form-urlencoded' }, body
        });
        status = r.status;
        if (!r.ok) { S.clipsMore = false; break; }
        const d = await r.json();
        for (const it of (d.items || [])) {
          const m = it.media || it; const row = project(m);
          const prev = S.rows.get(row.pk);
          if (prev) { if (row.plays != null) prev.plays = row.plays; }
          else S.rows.set(row.pk, row);
          merged++;
        }
        const pi = d.paging_info || {};
        S.clipsMore = !!pi.more_available;
        S.clipsCursor = pi.max_id || null;
        if (!S.clipsCursor) S.clipsMore = false;
        await sleep(400);
      }
      return { merged, collected: S.rows.size, more: S.clipsMore, status };
    },

    // Slim export in chunks — safe to return to the model / write to JSONL.
    dump(offset = 0, size = 200) {
      const all = [...S.rows.values()].sort((a, b) => b.taken_at - a.taken_at);
      return { total: all.length, offset, rows: all.slice(offset, offset + size) };
    }
  };
  return 'IGProf ready';
})();
