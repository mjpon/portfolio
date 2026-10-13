// Motion for the home page. Everything here answers something the visitor does,
// except the network map drawing itself once when the page opens.
// With "reduce motion" turned on, things still respond, but jump instead of moving.
import { animate, createTimeline, createDrawable, createMotionPath, spring, utils } from './vendor/anime.js';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
const snappy = spring({ bounce: 0.28, duration: 520 });

// Only one of the two drawings of the map is on screen at a time.
function shown(el) {
  return el.getClientRects().length > 0;
}

// ---------------------------------------------------------------------------
// Network map
// ---------------------------------------------------------------------------

// Opening sequence: the interchange appears, then each line is laid out from it by a
// train, and each station appears as its train passes. Trains run at one steady speed.
function drawNetwork(svg) {
  const hub = svg.querySelector('.hub');
  const lines = [...svg.querySelectorAll('.ln')];
  const stops = [...svg.querySelectorAll('.stop')];
  const template = svg.querySelector('.train');
  const speed = 1.1; // drawing units per millisecond

  const drawn = createDrawable(lines);
  utils.set(drawn, { draw: '0 0' });
  utils.set(hub, { scale: 0 });
  stops.forEach(stop => {
    utils.set(stop.querySelector('.sym'), { scale: 0 });
    utils.set(stop.querySelector('.lbl'), { opacity: 0 });
  });
  svg.classList.add('ready');

  const tl = createTimeline();
  tl.add(hub, { scale: [0, 1], ease: snappy }, 0);

  lines.forEach((line, i) => {
    const length = line.getTotalLength();
    const duration = length / speed;
    const start = 220 + i * 160;
    const train = template.cloneNode();
    template.after(train);

    tl.add(drawn[i], { draw: ['0 0', '0 1'], duration, ease: 'linear' }, start);
    tl.add(train, { ...createMotionPath(line), duration, ease: 'linear' }, start);
    tl.set(train, { opacity: 1 }, start);
    tl.add(train, { opacity: 0, duration: 220, ease: 'out(2)', onComplete: () => train.remove() }, start + duration);

    // A station appears when its train reaches it.
    stops.filter(s => s.dataset.line === line.dataset.line).forEach(stop => {
      const route = svg.querySelector(`.route[data-route="${stop.dataset.slug}"]`);
      const arrive = start + (route.getTotalLength() / length) * duration;
      tl.add(stop.querySelector('.sym'), { scale: [0, 1], ease: snappy }, arrive - 40);
      tl.add(stop.querySelector('.lbl'), { opacity: [0, 1], duration: 320, ease: 'out(2)' }, arrive + 60);
    });
  });
}

// Pointing at a station (or tabbing to it) sends a train from the interchange to it.
function wireDispatch(svg) {
  const train = svg.querySelector('.train');
  let trip = null;
  let fade = null;

  function dispatch(stop) {
    svg.dataset.focus = stop.dataset.line;
    if (fade) fade.pause();
    if (trip) trip.pause();
    const route = svg.querySelector(`.route[data-route="${stop.dataset.slug}"]`);
    const mark = stop.querySelector('.sym');
    if (reduced.matches) return;
    utils.set(train, { opacity: 1 });
    trip = animate(train, {
      ...createMotionPath(route),
      duration: 260 + route.getTotalLength() * 0.8,
      ease: 'inOut(2.4)',
      // The train pulls into the station, which answers with a small bump.
      onComplete: () => {
        animate(train, { opacity: 0, duration: 140, ease: 'out(2)' });
        animate(mark, { scale: [1.35, 1], ease: snappy });
      },
    });
  }

  function release() {
    delete svg.dataset.focus;
    fade = animate(train, { opacity: 0, duration: 260, delay: 120, ease: 'out(2)' });
  }

  svg.querySelectorAll('.stop').forEach(stop => {
    stop.addEventListener('pointerenter', () => dispatch(stop));
    stop.addEventListener('focus', () => dispatch(stop));
    stop.addEventListener('pointerleave', release);
    stop.addEventListener('blur', release);
  });
}

// The line chips under the map act as its legend: pointing at one brings its line forward.
function wireLegend(svgs) {
  document.querySelectorAll('.net .badge[data-line]').forEach(chip => {
    const on = () => svgs.forEach(svg => { svg.dataset.focus = chip.dataset.line; });
    const off = () => svgs.forEach(svg => { delete svg.dataset.focus; });
    chip.addEventListener('pointerenter', on);
    chip.addEventListener('focus', on);
    chip.addEventListener('pointerleave', off);
    chip.addEventListener('blur', off);
  });
}

// ---------------------------------------------------------------------------
// Work list: a red "you are here" ring rides each line's rail to the row in use.
// ---------------------------------------------------------------------------
function wireBoard(group) {
  const ring = document.createElement('span');
  ring.className = 'here';
  ring.setAttribute('aria-hidden', 'true');
  group.append(ring);
  let visible = false;

  function moveTo(row) {
    const box = row.getBoundingClientRect();
    const top = box.top - group.getBoundingClientRect().top + box.height / 2 - ring.offsetHeight / 2;
    if (!visible || reduced.matches) {
      utils.set(ring, { translateY: top });
      animate(ring, { opacity: 1, scale: reduced.matches ? 1 : [0.6, 1], duration: 200, ease: 'out(3)' });
      visible = true;
    } else {
      animate(ring, { translateY: top, ease: snappy });
    }
  }

  function hide() {
    visible = false;
    animate(ring, { opacity: 0, duration: 180, ease: 'out(2)' });
  }

  group.querySelectorAll('.row').forEach(row => {
    row.addEventListener('pointerenter', () => moveTo(row));
    row.addEventListener('focus', () => moveTo(row));
  });
  group.querySelector('.board').addEventListener('pointerleave', hide);
  group.addEventListener('focusout', event => {
    if (!group.contains(event.relatedTarget)) hide();
  });
}

// ---------------------------------------------------------------------------
// Route line: the page itself drawn as a line beside it. Each section is a stop, and a
// train moves down the line as the page scrolls. Through the Work section the line takes
// each project line's color. It is a mouse shortcut only: the header links do the same
// job for keyboards and screen readers, so it is hidden from them.
// ---------------------------------------------------------------------------
function routeLine() {
  const stops = [{ el: document.getElementById('top'), name: 'Start', kind: 'start', href: '#top' }];
  document.querySelectorAll('.group[data-line]').forEach(group => {
    const badge = group.querySelector('.line-head .badge');
    stops.push({
      el: group, name: badge.textContent.trim(), kind: 'line', line: group.dataset.line,
      href: '#' + group.id, shape: badge.querySelector('.st'),
    });
  });
  ['about', 'contact'].forEach(id => {
    const el = document.getElementById(id);
    if (el) stops.push({ el, name: el.querySelector('h2').textContent.trim(), kind: 'stop', href: '#' + id });
  });
  if (stops.some(s => !s.el)) return;

  const route = document.createElement('div');
  route.className = 'pageline';
  route.setAttribute('aria-hidden', 'true');
  const muted = document.createElement('div');
  const fill = document.createElement('div');
  muted.className = 'pageline-rail';
  fill.className = 'pageline-rail fill';
  route.append(muted, fill);

  stops.forEach(stop => {
    // Each stop owns the stretch of line after it, in its own color.
    [muted, fill].forEach(rail => {
      const seg = document.createElement('span');
      seg.className = 'seg';
      if (stop.line) seg.dataset.line = stop.line;
      rail.append(seg);
      (stop.segs = stop.segs || []).push(seg);
    });
    const link = document.createElement('a');
    link.className = 'pageline-stop ' + stop.kind;
    link.href = stop.href;
    link.tabIndex = -1;
    if (stop.line) link.dataset.line = stop.line;
    const mark = document.createElement('span');
    mark.className = 'pageline-mark';
    if (stop.shape) mark.append(stop.shape.cloneNode(true));
    const name = document.createElement('span');
    name.className = 'pageline-name';
    name.textContent = stop.name;
    link.append(mark, name);
    route.append(link);
    stop.link = link;
    stop.mark = mark;
  });

  const train = document.createElement('span');
  train.className = 'pageline-train';
  route.append(train);
  document.body.append(route);

  // Where each stop sits, both as a point in the page's scroll and as a point on the line.
  // A stop is reached when its section crosses the upper third of the screen, the same
  // point the header uses to underline the current section.
  let anchors = [];
  function measure() {
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const reading = window.innerHeight * 0.35;
    const scrolls = stops.map((stop, i) => {
      if (i === 0) return 0;
      const top = stop.el.getBoundingClientRect().top + window.scrollY;
      return Math.min(1, Math.max(0, (top - reading) / max));
    });
    // Stops that come too close on the line are spread apart so their names never overlap.
    const gap = Math.min(0.2, 30 / Math.max(1, route.clientHeight));
    const spots = scrolls.slice();
    for (let i = 1; i < spots.length; i++) spots[i] = Math.max(spots[i], spots[i - 1] + gap);
    for (let i = spots.length - 1; i >= 0; i--) spots[i] = Math.min(spots[i], 1 - gap * (spots.length - 1 - i));
    for (let i = 1; i < scrolls.length; i++) scrolls[i] = Math.max(scrolls[i], scrolls[i - 1] + 1e-6);
    anchors = stops.map((stop, i) => ({ scroll: scrolls[i], spot: spots[i] }));

    stops.forEach((stop, i) => {
      const from = spots[i];
      const to = i + 1 < spots.length ? spots[i + 1] : 1;
      stop.link.style.top = from * 100 + '%';
      stop.segs.forEach(seg => {
        seg.style.top = from * 100 + '%';
        seg.style.height = (to - from) * 100 + '%';
      });
    });
  }

  // Turns how far the page has scrolled into a point on the line, stop by stop.
  function spotFor(progress) {
    for (let i = anchors.length - 1; i >= 0; i--) {
      const a = anchors[i];
      if (progress >= a.scroll) {
        const b = anchors[i + 1];
        if (!b) return a.spot + (1 - a.spot) * Math.min(1, (progress - a.scroll) / Math.max(1e-6, 1 - a.scroll));
        return a.spot + (b.spot - a.spot) * ((progress - a.scroll) / (b.scroll - a.scroll));
      }
    }
    return 0;
  }

  let target = 0;
  let shown = 0;
  let frame = 0;
  let current = -1;

  function paint() {
    route.style.setProperty('--p', shown.toFixed(4));
    let now = 0;
    anchors.forEach((a, i) => {
      const passed = shown >= a.spot - 0.002;
      stops[i].link.classList.toggle('passed', passed);
      if (passed) now = i;
    });
    if (now !== current) {
      stops.forEach((stop, i) => stop.link.classList.toggle('current', i === now));
      // The stop answers with a small bump when the train pulls in. Not on the first paint.
      if (current !== -1 && now > current && !reduced.matches) {
        animate(stops[now].mark, { scale: [1.5, 1], ease: snappy });
      }
      current = now;
    }
  }

  // The train eases toward where the page is, so a fast scroll still reads as a ride.
  function step() {
    shown += (target - shown) * 0.2;
    if (Math.abs(target - shown) < 0.0005) {
      shown = target;
      frame = 0;
    } else {
      frame = requestAnimationFrame(step);
    }
    paint();
  }

  function update() {
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    target = spotFor(Math.min(1, Math.max(0, window.scrollY / max)));
    if (reduced.matches) {
      shown = target;
      paint();
    } else if (!frame) {
      frame = requestAnimationFrame(step);
    }
  }

  measure();
  shown = target = spotFor(Math.min(1, window.scrollY / Math.max(1, document.documentElement.scrollHeight - window.innerHeight)));
  paint();
  window.addEventListener('scroll', update, { passive: true });
  const relayout = () => { measure(); update(); };
  window.addEventListener('resize', relayout);
  new ResizeObserver(relayout).observe(document.body);
}

// ---------------------------------------------------------------------------

routeLine();

const svgs = [...document.querySelectorAll('.net > svg')];
svgs.forEach(svg => {
  if (!reduced.matches && shown(svg)) drawNetwork(svg);
  else svg.classList.add('ready');
  wireDispatch(svg);
});
wireLegend(svgs);
document.querySelectorAll('.group').forEach(wireBoard);
