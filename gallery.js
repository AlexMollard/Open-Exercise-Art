// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Alex Mollard
const gallery = document.getElementById('gallery');
const search = document.getElementById('search');
const count = document.getElementById('count');
let exercises = [];

function render() {
  const query = search.value.trim().toLocaleLowerCase();
  const matches = exercises.filter(exercise =>
    [exercise.name, exercise.id, ...exercise.aliases].some(value => value.toLocaleLowerCase().includes(query))
  );
  gallery.replaceChildren();
  const fragment = document.createDocumentFragment();
  for (const exercise of matches) {
    const card = document.createElement('article');
    card.className = 'card';
    const preview = document.createElement('div');
    preview.className = 'preview';
    const image = document.createElement('img');
    image.src = exercise.svg.file;
    image.alt = exercise.name + ' illustration';
    image.loading = 'lazy';
    image.decoding = 'async';
    preview.append(image);
    const details = document.createElement('div');
    details.className = 'details';
    const name = document.createElement('h2');
    name.textContent = exercise.name;
    const downloads = document.createElement('div');
    downloads.className = 'downloads';
    for (const format of ['svg', 'png']) {
      const link = document.createElement('a');
      link.href = exercise[format].file;
      link.download = exercise.id + '.' + format;
      link.textContent = format.toUpperCase() + ' ↓';
      link.setAttribute('aria-label', 'Download ' + exercise.name + ' as ' + format.toUpperCase());
      downloads.append(link);
    }
    details.append(name, downloads);
    card.append(preview, details);
    fragment.append(card);
  }
  gallery.append(fragment);
  count.textContent = matches.length + ' of ' + exercises.length + ' illustrations' + (matches.length ? '' : ' · No matching exercises');
}

search.addEventListener('input', render);
fetch('catalogue.json')
  .then(response => {
    if (!response.ok) throw new Error('Catalogue could not be loaded');
    return response.json();
  })
  .then(catalogue => {
    exercises = catalogue.exercises.sort((a, b) => a.name.localeCompare(b.name));
    render();
  })
  .catch(() => {
    count.textContent = 'Gallery unavailable';
    const error = document.getElementById('error');
    error.hidden = false;
    error.textContent = 'Serve this folder with python -m http.server 8000 --bind 127.0.0.1, or browse INDEX.md on GitHub.';
  });
