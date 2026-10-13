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

const svgs = [...document.querySelectorAll('.net > svg')];
svgs.forEach(svg => {
  if (!reduced.matches && shown(svg)) drawNetwork(svg);
  else svg.classList.add('ready');
  wireDispatch(svg);
});
wireLegend(svgs);
document.querySelectorAll('.group').forEach(wireBoard);
