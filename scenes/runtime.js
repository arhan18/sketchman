/* Shared scene runtime: builds the shot DOM, applies the series palette, and
   exposes seek(t) for deterministic frame-accurate capture. Styles only supply
   SKETCHMAN_STYLE.renderShot(clip, series, index). */
(function () {
  const P = window.PAYLOAD;
  const S = window.SKETCHMAN_STYLE;
  const root = document.documentElement;

  ['background', 'surface', 'ink', 'accent', 'muted'].forEach(function (key) {
    root.style.setProperty('--' + key, P.series[key]);
  });
  root.style.setProperty('--stage-w', P.size.w + 'px');
  root.style.setProperty('--stage-h', P.size.h + 'px');
  document.body.className = 'series-' + P.series.id
    + (P.size.h > P.size.w ? ' vertical' : '');

  const stage = document.getElementById('stage');

  P.clips.forEach(function (clip, i) {
    const el = document.createElement('section');
    el.className = 'shot scene-' + clip.scene;
    el.dataset.start = clip.start;
    el.dataset.end = clip.end;
    el.dataset.index = i;
    el.innerHTML = S.renderShot(clip, P.series, i);
    if (clip.caption) {
      const cap = document.createElement('div');
      cap.className = 'caption';
      const line = document.createElement('span');
      line.className = 'caption-line';
      line.textContent = clip.caption;
      const n = clip.caption.length;
      line.style.setProperty('--cap-scale', n > 150 ? 0.60 : n > 110 ? 0.68 : n > 72 ? 0.80 : 0.92);
      cap.appendChild(line);
      el.appendChild(cap);
    }
    stage.appendChild(el);
  });

  const shots = Array.prototype.slice.call(stage.querySelectorAll('.shot'));

  window.seek = function (t) {
    for (let i = 0; i < shots.length; i++) {
      const s = shots[i];
      const start = parseFloat(s.dataset.start);
      const end = parseFloat(s.dataset.end);
      s.classList.toggle('active', t >= start && t < end);
      s.classList.toggle('past', t >= end);
      s.classList.toggle('future', t < start);
    }
    const anims = document.getAnimations();
    for (let i = 0; i < anims.length; i++) {
      const a = anims[i];
      const target = a.effect && a.effect.target;
      const host = target && target.closest ? target.closest('.shot') : null;
      a.pause();
      if (!host) { a.currentTime = 0; continue; }
      const local = (t - parseFloat(host.dataset.start)) * 1000;
      a.currentTime = local < 0 ? 0 : local;
    }
  };

  if (S.init) S.init(P);
  document.getAnimations().forEach(function (a) { a.pause(); a.currentTime = 0; });
  window.seek(0);
  window.SKETCHMAN_READY = true;
})();
