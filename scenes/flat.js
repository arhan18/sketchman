/* Flat-cartoon illustration library.
   The drawing language: flat colour fields, dark outlines with a slight hand
   wobble, two or three colours per scene, no gradients except skies. Used by
   the Arjun (educational) and Mira (conceptual) templates, which share this
   medium but stage it differently.

   Everything returns an SVG string sized on a 1280x720 stage. */
window.FLAT = (function () {
  var INK = "#2a2118";
  var W = 1280, H = 720;

  function open(inner, extra) {
    return '<svg class="flat" viewBox="0 0 ' + W + ' ' + H + '" width="100%" height="100%" '
      + (extra || "") + '>' + inner + '</svg>';
  }
  function wob(pts, close) {
    // slight hand wobble between points
    var d = "M" + pts[0][0] + " " + pts[0][1];
    for (var i = 1; i < pts.length; i++) {
      var a = pts[i - 1], b = pts[i];
      var mx = (a[0] + b[0]) / 2 + (i % 2 ? 1.4 : -1.4);
      var my = (a[1] + b[1]) / 2 + (i % 2 ? -1.2 : 1.2);
      d += " Q" + mx.toFixed(1) + " " + my.toFixed(1) + " " + b[0] + " " + b[1];
    }
    return d + (close ? " Z" : "");
  }
  function ground(fill, y) {
    return '<path d="' + wob([[0, y + 6], [320, y - 8], [660, y + 4], [980, y - 6], [1280, y + 2], [1280, H], [0, H]], true)
      + '" fill="' + fill + '"/>';
  }
  function sky(top, bottom) {
    return '<defs><linearGradient id="fs" x1="0" y1="0" x2="0" y2="1">'
      + '<stop offset="0%" stop-color="' + top + '"/><stop offset="100%" stop-color="' + bottom + '"/>'
      + '</linearGradient></defs><rect width="' + W + '" height="' + H + '" fill="url(#fs)"/>';
  }
  function grass(y) {
    var s = "";
    for (var i = 0; i < 16; i++) {
      var x = 40 + i * 82, h = 12 + (i % 4) * 5;
      s += '<path d="M' + x + ' ' + y + ' q4 -' + h + ' 8 0" fill="none" stroke="' + INK + '" stroke-width="2.5" opacity=".45"/>';
    }
    return s;
  }
  function tuft(x, y) {
    return '<g fill="none" stroke="' + INK + '" stroke-width="3" opacity=".5" stroke-linecap="round">'
      + '<path d="M' + x + ' ' + y + ' q6 -10 12 0"/><path d="M' + (x + 20) + ' ' + y + ' q6 -12 13 0"/></g>';
  }

  /* --- characters: flat, outlined, big head, simple limbs --- */
  function kid(x, y, s, pose) {
    pose = pose || "stand";
    var arm = pose === "point"
      ? '<path d="M64 150 q46 -18 78 -52" fill="none" stroke="#3f6ea8" stroke-width="15" stroke-linecap="round"/>'
      : pose === "hold"
        ? '<path d="M42 156 q42 26 84 0" fill="none" stroke="#3f6ea8" stroke-width="15" stroke-linecap="round"/>'
        : '<path d="M30 152 q-6 40 -2 62" fill="none" stroke="#3f6ea8" stroke-width="15" stroke-linecap="round"/>'
          + '<path d="M126 152 q6 40 2 62" fill="none" stroke="#3f6ea8" stroke-width="15" stroke-linecap="round"/>';
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<ellipse cx="78" cy="246" rx="66" ry="12" fill="' + INK + '" opacity=".12"/>'
      + arm
      + '<path d="M26 250 q0 -104 52 -104 t52 104 z" fill="#3f6ea8" stroke="' + INK + '" stroke-width="4" stroke-linejoin="round"/>'
      + '<path d="M62 146 h32 l-4 22 h-24 z" fill="#f0c9a4" stroke="' + INK + '" stroke-width="3"/>'
      + '<circle cx="78" cy="96" r="46" fill="#f6d3ae" stroke="' + INK + '" stroke-width="4"/>'
      + '<path d="' + wob([[32, 92], [40, 60], [74, 50], [108, 56], [124, 92], [100, 76], [60, 74]], true)
      + '" fill="#3b2f2a" stroke="' + INK + '" stroke-width="3"/>'
      + '<circle cx="64" cy="98" r="4.5" fill="' + INK + '"/><circle cx="94" cy="98" r="4.5" fill="' + INK + '"/>'
      + '<path d="M66 116 q12 9 24 -2" fill="none" stroke="' + INK + '" stroke-width="4" stroke-linecap="round"/>'
      + '</g>';
  }
  function girl(x, y, s, pose) {
    pose = pose || "stand";
    var magnifier = pose === "look"
      ? '<circle cx="132" cy="150" r="30" fill="#ffffff" opacity=".85" stroke="#e4572e" stroke-width="6"/>'
        + '<path d="M154 172 l26 26" stroke="#e4572e" stroke-width="8" stroke-linecap="round"/>'
      : "";
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<ellipse cx="76" cy="244" rx="60" ry="11" fill="' + INK + '" opacity=".12"/>'
      + '<path d="M30 150 q-4 38 0 58" fill="none" stroke="#e4572e" stroke-width="14" stroke-linecap="round"/>'
      + '<path d="M122 150 q4 38 0 58" fill="none" stroke="#e4572e" stroke-width="14" stroke-linecap="round"/>'
      + '<path d="M26 250 q0 -100 50 -100 t50 100 z" fill="#e4572e" stroke="' + INK + '" stroke-width="4" stroke-linejoin="round"/>'
      + '<path d="M60 148 h32 l-4 20 h-24 z" fill="#f0c9a4" stroke="' + INK + '" stroke-width="3"/>'
      + '<circle cx="76" cy="98" r="44" fill="#f6d3ae" stroke="' + INK + '" stroke-width="4"/>'
      + '<path d="' + wob([[32, 96], [36, 56], [76, 44], [116, 58], [120, 100], [96, 74], [58, 76]], true)
      + '" fill="#4a3428" stroke="' + INK + '" stroke-width="3"/>'
      + '<circle cx="62" cy="100" r="4.5" fill="' + INK + '"/><circle cx="92" cy="100" r="4.5" fill="' + INK + '"/>'
      + '<path d="M64 118 q12 9 24 -2" fill="none" stroke="' + INK + '" stroke-width="4" stroke-linecap="round"/>'
      + magnifier + '</g>';
  }

  /* --- props --- */
  function jar(x, y, s, fill) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<path d="M-70 -40 h140 v150 a34 34 0 0 1 -34 34 h-72 a34 34 0 0 1 -34 -34z" fill="#f6efe0" stroke="' + INK + '" stroke-width="5"/>'
      + '<rect x="-82" y="-64" width="164" height="30" rx="10" fill="#3f6ea8" stroke="' + INK + '" stroke-width="5"/>'
      + '<path d="M-58 46 h116 v58 a26 26 0 0 1 -26 26 h-64 a26 26 0 0 1 -26 -26z" fill="' + (fill || "#f2c14e") + '"/>'
      + '<g fill="#f6d76a" stroke="' + INK + '" stroke-width="3">'
      + '<circle cx="-24" cy="78" r="17"/><circle cx="10" cy="92" r="19"/>'
      + '<circle cx="44" cy="74" r="16"/></g></g>';
  }
  function coinStack(n, cx) {
    var s = "";
    for (var i = 0; i < n; i++) {
      s += '<ellipse cx="' + cx + '" cy="' + (470 - i * 18) + '" rx="54" ry="17" fill="#f2c14e" stroke="' + INK + '" stroke-width="4"/>';
    }
    return s;
  }
  function phone(x, y, s) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<rect x="0" y="0" width="180" height="330" rx="26" fill="#2f3b52" stroke="' + INK + '" stroke-width="5"/>'
      + '<rect x="18" y="52" width="144" height="220" rx="12" fill="#dfe9f2"/>'
      + '<rect x="34" y="74" width="86" height="14" rx="7" fill="#3f6ea8"/>'
      + '<rect x="34" y="104" width="112" height="14" rx="7" fill="#9fb2c6"/>'
      + '<rect x="34" y="134" width="96" height="14" rx="7" fill="#9fb2c6"/>'
      + '<rect x="34" y="176" width="60" height="34" rx="8" fill="#3f6ea8"/>'
      + '</g>';
  }
  function bars(values, labels) {
    var max = Math.max.apply(null, values) || 1;
    var out = "", w = 120, gap = 46, x0 = 210;
    values.forEach(function (v, i) {
      var h = Math.max(30, (v / max) * 300);
      var x = x0 + i * (w + gap);
      out += '<rect x="' + x + '" y="' + (500 - h) + '" width="' + w + '" height="' + h + '" rx="10" fill="#3f6ea8" stroke="' + INK + '" stroke-width="5"/>';
      if (labels && labels[i]) {
        out += '<text x="' + (x + w / 2) + '" y="546" text-anchor="middle" font-family="Georgia, serif" font-size="30" fill="' + INK + '">' + labels[i] + '</text>';
      }
    });
    out += '<path d="M160 500 h960" stroke="' + INK + '" stroke-width="5" stroke-linecap="round"/>';
    return out;
  }
  function calendar(x, y, s) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<rect x="0" y="0" width="280" height="240" rx="16" fill="#fdf7ea" stroke="' + INK + '" stroke-width="5"/>'
      + '<rect x="0" y="0" width="280" height="60" rx="16" fill="#3f6ea8" stroke="' + INK + '" stroke-width="5"/>'
      + '<g fill="#9fb2c6">'
      + '<rect x="26" y="86" width="46" height="36" rx="8"/><rect x="88" y="86" width="46" height="36" rx="8"/>'
      + '<rect x="150" y="86" width="46" height="36" rx="8" fill="#e4572e"/><rect x="212" y="86" width="42" height="36" rx="8"/>'
      + '<rect x="26" y="140" width="46" height="36" rx="8"/><rect x="88" y="140" width="46" height="36" rx="8"/>'
      + '<rect x="150" y="140" width="46" height="36" rx="8"/><rect x="212" y="140" width="42" height="36" rx="8"/></g>'
      + '</g>';
  }
  function mug(x, y, s) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<path d="M0 0 h120 v96 a30 30 0 0 1 -30 30 h-60 a30 30 0 0 1 -30 -30z" fill="#e4572e" stroke="' + INK + '" stroke-width="5"/>'
      + '<path d="M120 20 q52 0 52 40 t-52 40" fill="none" stroke="' + INK + '" stroke-width="5"/>'
      + '<path d="M-10 -22 q14 -20 4 -34 M30 -22 q14 -20 4 -34 M70 -22 q14 -20 4 -34" fill="none" stroke="' + INK + '" stroke-width="4" opacity=".5" stroke-linecap="round"/>'
      + '</g>';
  }
  function ledger(x, y, s, open_) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + (open_
        ? '<path d="M0 0 h150 q30 10 30 40 v170 q-30 -30 -30 -30 H0z" fill="#fdf7ea" stroke="' + INK + '" stroke-width="5"/>'
          + '<path d="M330 0 h-150 q-30 10 -30 40 v170 q30 -30 30 -30 h150z" fill="#fdf7ea" stroke="' + INK + '" stroke-width="5"/>'
          + '<g stroke="#9fb2c6" stroke-width="5" stroke-linecap="round">'
          + '<path d="M200 60 h100M200 100 h100M200 140 h76"/></g>'
        : '<rect x="0" y="0" width="330" height="210" rx="14" fill="#3f6ea8" stroke="' + INK + '" stroke-width="5"/>'
          + '<rect x="24" y="24" width="282" height="60" rx="10" fill="#fdf7ea"/>')
      + '</g>';
  }
  function door(x, y, s, open_) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<rect x="0" y="0" width="230" height="330" rx="8" fill="' + (open_ ? "#f2c14e" : "#3f6ea8") + '" stroke="' + INK + '" stroke-width="5"/>'
      + (open_ ? '<path d="M0 330 L230 0" fill="none" stroke="#fdf7ea" stroke-width="10" opacity=".8"/>'
        : '<circle cx="196" cy="170" r="12" fill="#fdf7ea" stroke="' + INK + '" stroke-width="4"/>')
      + '</g>';
  }

  /* --- background furniture: density, so frames read like the references --- */
  function shelf(x, y, s) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<rect x="0" y="0" width="420" height="18" rx="6" fill="#c9a97e" stroke="' + INK + '" stroke-width="4"/>'
      + '<rect x="0" y="96" width="420" height="18" rx="6" fill="#c9a97e" stroke="' + INK + '" stroke-width="4"/>'
      + '<g fill="#7fa5c9" stroke="' + INK + '" stroke-width="3">'
      + '<rect x="20" y="-72" width="22" height="72" rx="4"/><rect x="48" y="-60" width="20" height="60" rx="4"/>'
      + '<rect x="74" y="-80" width="24" height="80" rx="4"/></g>'
      + '<g fill="#e8d7b5" stroke="' + INK + '" stroke-width="3">'
      + '<rect x="180" y="-58" width="90" height="58" rx="5"/></g>'
      + '<circle cx="330" cy="-34" r="34" fill="#e0713f" stroke="' + INK + '" stroke-width="4"/>'
      + '<path d="M330 -68 v-14" stroke="' + INK + '" stroke-width="4"/>'
      + '<g fill="#9fb2c6" stroke="' + INK + '" stroke-width="3">'
      + '<rect x="30" y="22" width="60" height="40" rx="5"/><rect x="100" y="34" width="52" height="34" rx="5"/>'
      + '<circle cx="230" cy="52" r="30" fill="#f2c14e"/></g></g>';
  }
  function plant(x, y, s) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<path d="M-46 0 h92 l-12 74 h-68z" fill="#c9704c" stroke="' + INK + '" stroke-width="4"/>'
      + '<g fill="#4f8f5b" stroke="' + INK + '" stroke-width="4">'
      + '<path d="M0 -6 q-6 -70 -52 -78 q34 44 40 78z"/>'
      + '<path d="M0 -6 q10 -84 58 -88 q-38 46 -44 88z"/>'
      + '<path d="M0 -6 q-4 -52 4 -96 q14 46 8 96z"/></g></g>';
  }
  function books(x, y, s) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<g stroke="' + INK + '" stroke-width="4">'
      + '<rect x="0" y="-34" width="150" height="34" rx="6" fill="#e0713f"/>'
      + '<rect x="10" y="-66" width="140" height="32" rx="6" fill="#7fa5c9"/>'
      + '<rect x="4" y="-96" width="146" height="30" rx="6" fill="#f2c14e"/></g></g>';
  }
  function papers(x, y, s, rot) {
    return '<g transform="translate(' + x + ' ' + y + ') rotate(' + (rot || 0) + ') scale(' + s + ')" opacity=".95">'
      + '<rect x="0" y="0" width="150" height="110" rx="6" fill="#fdf7ea" stroke="' + INK + '" stroke-width="4"/>'
      + '<g stroke="#9fb2c6" stroke-width="4" stroke-linecap="round">'
      + '<path d="M20 28 h100M20 52 h84M20 76 h104"/></g></g>';
  }
  function laptop(x, y, s) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<path d="M0 0 l330 0 l-42 -230 h-246z" fill="#2f3b52" stroke="' + INK + '" stroke-width="5"/>'
      + '<path d="M20 -18 h290 l-32 -194 h-226z" fill="#8fb4cc"/>'
      + '<rect x="-40" y="0" width="410" height="18" rx="9" fill="#3f4a5c" stroke="' + INK + '" stroke-width="5"/></g>';
  }
  function coinPile(x, y, s) {
    var out = "";
    for (var i = 0; i < 5; i++) {
      out += '<ellipse cx="' + x + '" cy="' + (y - i * 15) + '" rx="' + (46 - i * 3) + '" ry="15" fill="#f2c14e" stroke="' + INK + '" stroke-width="4"/>';
    }
    return out;
  }
  function rug(cx, cy, rx) {
    return '<ellipse cx="' + cx + '" cy="' + cy + '" rx="' + rx + '" ry="' + (rx * 0.22) + '" fill="#d9b98f" opacity=".55" stroke="' + INK + '" stroke-width="4"/>';
  }
  function windowFlat(x, y, s) {
    return '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ')">'
      + '<rect x="0" y="0" width="300" height="220" rx="10" fill="#cfe3ef" stroke="' + INK + '" stroke-width="5"/>'
      + '<path d="M150 0 v220M0 110 h300" stroke="' + INK + '" stroke-width="4"/>'
      + '<circle cx="238" cy="46" r="26" fill="#f2c14e"/></g>';
  }
  /* A filled room: back wall, window, shelf, rug, plant, books. */
  function roomDense() {
    return sky('#f7efdc', '#fbf6e8')
      + ground('#e9dcc0', 520) + grass(520)
      + windowFlat(940, 90, 0.9)
      + shelf(120, 470, 0.78)
      + rug(640, 610, 320)
      + plant(1160, 500, 0.8)
      + books(760, 520, 0.8);
  }

  return {
    W: W, H: H, INK: INK, open: open, wob: wob, sky: sky, ground: ground,
    grass: grass, tuft: tuft, kid: kid, girl: girl, jar: jar, phone: phone,
    coinStack: coinStack, bars: bars, calendar: calendar, mug: mug,
    ledger: ledger, door: door, shelf: shelf, plant: plant, books: books,
    papers: papers, laptop: laptop, coinPile: coinPile, rug: rug,
    windowFlat: windowFlat, roomDense: roomDense
  };
})();
