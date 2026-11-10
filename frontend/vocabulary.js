const vocabulary = (() => {
  const storagePrefix = "g-study-room:vocabulary:v1:";
  const storageKey = testKey => storagePrefix + testKey;
  const clean = text => text.replace(/\s+/g, " ").trim();
  const wordKey = text => clean(text).normalize("NFKC").toLowerCase();
  const maxSelectionLength = 180;

  function read(testKey) {
    const saved = localStorage.getItem(storageKey(testKey));
    return saved ? JSON.parse(saved) : [];
  }

  function update(testKey, edit) {
    const entries = read(testKey);
    edit(entries);
    localStorage.setItem(storageKey(testKey), JSON.stringify(entries));
  }

  function add(testKey, passage, title, selection, context) {
    const text = clean(selection);
    const key = wordKey(text);
    const entry = {passage, title, key, text, context: clean(context), note: ""};
    const existing = read(testKey).find(item => item.passage === passage && item.key === key);
    if (!existing) update(testKey, entries => entries.unshift(entry));
    return key;
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function open({title, tests, passage, focusKey}) {
    const dialog = element("dialog", "vocab-dialog");
    dialog.setAttribute("aria-labelledby", "vocab-title");
    const bar = element("div", "vocab-dialog-bar");
    const heading = element("h2", "", title);
    heading.id = "vocab-title";
    const close = element("button", "vocab-button", "Close");
    close.type = "button";
    close.onclick = () => dialog.close();
    bar.append(heading, close);
    const list = element("div", "vocab-list");
    const notice = element("p", "vocab-notice");
    notice.setAttribute("role", "status");
    dialog.append(bar);
    let search;
    if (passage === undefined) {
      search = element("input", "vocab-search");
      search.type = "search";
      search.placeholder = "Search words, phrases or notes";
      search.setAttribute("aria-label", search.placeholder);
      dialog.append(search);
    }
    dialog.append(notice, list);

    function render() {
      list.replaceChildren();
      const query = wordKey(search?.value ?? "");
      let focusedNote;
      try {
        let total = 0;
        for (const test of tests) {
          const byPassage = new Map();
          const entries = read(test.key).filter(item =>
            (passage === undefined || passage === item.passage) &&
            wordKey(item.text + " " + item.note).includes(query));
          for (const entry of entries) {
            if (!byPassage.has(entry.passage)) byPassage.set(entry.passage, []);
            byPassage.get(entry.passage).push(entry);
          }
          for (const [index, words] of [...byPassage].sort(([a], [b]) => a - b)) {
            total += words.length;
            const group = element("section", "vocab-group");
            if (passage === undefined) {
              const groupBar = element("div", "vocab-group-bar");
              groupBar.append(element("h3", "", test.label + " · " + words[0].title));
              const url = new URL(test.url, location.href);
              url.searchParams.set("passage", index);
              const link = element("a", "", "Open passage");
              link.href = url.href;
              groupBar.append(link);
              group.append(groupBar);
            }
            for (const entry of words) {
              const card = element("article", "vocab-entry");
              const word = element("div", "vocab-word", entry.text);
              const context = element("p", "vocab-context", entry.context);
              const label = element("label", "vocab-note", "Meaning or notes");
              const note = element("textarea", "");
              note.value = entry.note;
              note.rows = 2;
              note.maxLength = 2000;
              note.placeholder = "Add your own explanation";
              const feedback = element("span", "vocab-feedback");
              feedback.setAttribute("role", "status");
              const remove = element("button", "vocab-button vocab-remove", "Remove");
              remove.type = "button";
              remove.setAttribute("aria-label", "Remove " + entry.text);
              const matches = item => item.passage === entry.passage && item.key === entry.key;
              note.oninput = () => {
                try {
                  update(test.key, items => {
                    const saved = items.find(matches);
                    if (!saved) throw new Error("Entry removed");
                    saved.note = note.value;
                  });
                  feedback.textContent = "Saved";
                } catch {
                  feedback.textContent = "Could not save this note. Reopen the notebook or try again.";
                }
              };
              remove.onclick = () => {
                try {
                  update(test.key, items => {
                    const index = items.findIndex(matches);
                    if (index >= 0) items.splice(index, 1);
                  });
                  render();
                  (search || close).focus();
                } catch {
                  feedback.textContent = "Could not remove this entry.";
                }
              };
              label.append(note);
              const actions = element("div", "vocab-entry-actions");
              actions.append(remove, feedback);
              card.append(word, context, label, actions);
              group.append(card);
              if (entry.key === focusKey) focusedNote = note;
            }
            list.append(group);
          }
        }
        notice.textContent = total ? total + (total === 1 ? " entry" : " entries") :
          query ? "No matches." : passage === undefined ? "No words saved in this book yet." :
            "Select a word or phrase in this passage and choose Add to vocabulary.";
      } catch {
        notice.textContent = "This browser could not open the saved vocabulary.";
      }
      return focusedNote;
    }

    if (search) search.oninput = () => render();
    dialog.addEventListener("close", () => dialog.remove(), {once: true});
    document.body.append(dialog);
    const note = render();
    dialog.showModal();
    (note || search || close).focus();
  }

  return {add, open, maxSelectionLength};
})();
