(() => {
  "use strict";
  const { c, providers, towns, provider, prefix, type } = window.PROTOTYPE;
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  window.lucide.createIcons();

  const menu = $("#mobile-menu");
  $("#menu-toggle").addEventListener("click", () => {
    menu.hidden = !menu.hidden;
    $("#menu-toggle").setAttribute("aria-expanded", String(!menu.hidden));
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !menu.hidden) {
      menu.hidden = true;
      $("#menu-toggle").setAttribute("aria-expanded", "false");
      $("#menu-toggle").focus();
    }
  });
  matchMedia("(min-width:1000px)").addEventListener("change", (e) => {
    if (e.matches) {
      menu.hidden = true;
      $("#menu-toggle").setAttribute("aria-expanded", "false");
    }
  });

  // Preserve only the prototype's documented GET fields across language links.
  const params = new URLSearchParams(location.search);
  const safeParams = new URLSearchParams();
  for (const key of ["q", "category", "district", "town"]) {
    if (params.has(key)) safeParams.set(key, params.get(key).slice(0, 200));
  }
  $$(".language-switch a").forEach((a) => {
    const url = new URL(a.href);
    url.search = safeParams.toString();
    a.href = url.href;
  });

  const normalize = (text) =>
    text
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  const alias = {
    plumbing: [
      "plumber",
      "plumbers",
      "plumbing",
      "plomero",
      "plomeros",
      "plomeria",
    ],
    carpentry: [
      "carpenter",
      "carpenters",
      "carpentry",
      "carpintero",
      "carpinteria",
    ],
  };
  function parseQuery(query) {
    let remaining = normalize(query);
    const parsed = {
      category: "",
      district: "",
      town: "",
      urgent: /\b(tonight|esta noche)\b/.test(remaining),
    };
    const consume = (values) => {
      for (const item of [...values].sort((a, b) => b.length - a.length)) {
        const normalized = normalize(item);
        const at = remaining.indexOf(normalized);
        if (
          at >= 0 &&
          !/[a-z]/.test(remaining[at - 1] || "") &&
          !/[a-z]/.test(remaining[at + normalized.length] || "")
        ) {
          remaining =
            remaining.slice(0, at) +
            " " +
            remaining.slice(at + normalized.length);
          return item;
        }
      }
      return "";
    };
    for (const [key, values] of Object.entries(alias)) {
      if (consume(values)) {
        parsed.category = key;
        break;
      }
    }
    parsed.town = consume(Object.values(towns).flat());
    parsed.district = consume(Object.keys(towns));
    if (!parsed.district && parsed.town)
      parsed.district = Object.keys(towns).find((d) =>
        towns[d].includes(parsed.town),
      );
    remaining = remaining.replace(
      /\b(i need|necesito|tonight|esta noche|a|an|un|una|in|en|de|the|please|por favor)\b/g,
      " ",
    );
    parsed.terms = remaining.trim().split(/\s+/).filter(Boolean);
    return parsed;
  }
  const searchForm = $(".search-form");
  if (searchForm) {
    const district = $("[name=district]", searchForm);
    const town = $("[name=town]", searchForm);
    const setTowns = (value) => {
      const previous = town.value;
      town.replaceChildren(new Option(c.allTowns, ""));
      (towns[value] || Object.values(towns).flat()).forEach((t) =>
        town.add(new Option(t, t)),
      );
      town.value = [...town.options].some((o) => o.value === previous)
        ? previous
        : "";
    };
    district.addEventListener("change", () => setTowns(district.value));
    if (type === "results") {
      if (matchMedia("(max-width:699px)").matches)
        $(".filters", searchForm).open = false;
      const q = (params.get("q") || "").slice(0, 200);
      const parsed = parseQuery(q);
      const categoryValue = params.has("category")
        ? params.get("category")
        : parsed.category;
      const districtValue = params.has("district")
        ? params.get("district")
        : parsed.district;
      const townValue = params.has("town") ? params.get("town") : parsed.town;
      const category = $("[name=category]", searchForm);
      $("#need").value = q;
      category.value = categoryValue;
      district.value = districtValue;
      setTowns(districtValue);
      town.value = townValue;
      const valid =
        (!categoryValue || Object.hasOwn(alias, categoryValue)) &&
        (!districtValue || Object.hasOwn(towns, districtValue)) &&
        (!townValue ||
          (towns[districtValue] || Object.values(towns).flat()).includes(
            townValue,
          ));
      let count = 0;
      $$(".provider-card").forEach((card) => {
        const p = providers.find((p) => p.id === card.dataset.provider);
        const haystack = normalize(
          `${p.name} ${p.category} ${p.district} ${p.towns.join(" ")}`,
        );
        const match =
          valid &&
          (!categoryValue || p.category === categoryValue) &&
          (!districtValue || p.district === districtValue) &&
          (!townValue || p.towns.includes(townValue)) &&
          parsed.terms.every((term) => haystack.includes(term));
        card.hidden = !match;
        if (match) count++;
      });
      $("#result-count").textContent = count;
      $("#result-count").nextSibling.textContent =
        ` ${count === 1 ? (document.documentElement.lang === "es" ? "proveedor" : "provider") : c.resultCount}`;
      $("#empty-state").hidden = count > 0;
      $("#results-grid").hidden = count === 0;
      $("#urgency").hidden = !parsed.urgent;
      const context = $("#search-context");
      const labels = [
        categoryValue && (c[categoryValue] || categoryValue),
        districtValue,
        townValue,
      ];
      context.hidden = !q && !labels.some(Boolean);
      if (!context.hidden) {
        const title = document.createElement("strong");
        title.textContent = c.matched;
        context.append(title);
        labels.filter(Boolean).forEach((label) => {
          const el = document.createElement("span");
          el.textContent = label;
          context.append(el);
        });
        const reset = document.createElement("a");
        reset.href = "results.html";
        reset.textContent = c.clear;
        context.append(reset);
      }
    }
    searchForm.addEventListener("submit", (e) => {
      // Empty selects must not override category/area inference from the main ask.
      e.preventDefault();
      const next = new URL("results.html", location.href);
      const data = new FormData(searchForm);
      for (const [key, value] of data)
        if (String(value).trim())
          next.searchParams.set(key, String(value).trim());
      location.href = next.href;
    });
  }

  let opener;
  $$("[data-open]").forEach((button) =>
    button.addEventListener("click", () => {
      opener = button;
      const dialog = document.getElementById(button.dataset.open);
      dialog.showModal();
      if (button.dataset.start === "manage") $("[data-stage=manage]").click();
      if (button.dataset.open === "pros") {
        menu.hidden = true;
        $("#menu-toggle").setAttribute("aria-expanded", "false");
      }
    }),
  );
  $$("[data-close]").forEach((button) =>
    button.addEventListener("click", () => button.closest("dialog").close()),
  );
  $$("dialog").forEach((dialog) => {
    dialog.addEventListener("close", () => {
      if (dialog.id === "quote") resetQuote();
      if (opener?.isConnected && opener.getClientRects().length) opener.focus();
      else $("#menu-toggle").focus();
    });
    dialog.addEventListener("click", (e) => {
      if (e.target === dialog) {
        const bounds = dialog.getBoundingClientRect();
        if (
          e.clientX < bounds.left ||
          e.clientX > bounds.right ||
          e.clientY < bounds.top ||
          e.clientY > bounds.bottom
        )
          dialog.close();
      }
    });
  });
  let photoIndex = 0;
  $$("[data-photo]").forEach((button) =>
    button.addEventListener("click", () => {
      photoIndex =
        (photoIndex + Number(button.dataset.photo) + provider.photos.length) %
        provider.photos.length;
      $("#gallery-image").src =
        `${prefix}assets/${provider.photos[photoIndex]}`;
      $("#photo-count").textContent =
        `${photoIndex + 1} / ${provider.photos.length}`;
    }),
  );

  const quoteForm = $("#quote-form");
  const method = $("[name=method]", quoteForm),
    contact = $("[name=contact]", quoteForm);
  method.addEventListener("change", () => {
    contact.type = method.value === "email" ? "email" : "tel";
  });
  quoteForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!quoteForm.reportValidity()) return;
    const data = new FormData(quoteForm);
    if (data.get("consent") !== "on") return;
    const summary = $("#quote-summary");
    summary.replaceChildren();
    for (const [label, value] of [
      [c.need, data.get("need")],
      [c.town, data.get("area")],
      [
        c.contactMethod,
        `${method.selectedOptions[0].textContent}: ${data.get("contact")}`,
      ],
      [c.consented, provider.name],
    ]) {
      const dt = document.createElement("dt"),
        dd = document.createElement("dd");
      dt.textContent = label;
      dd.textContent = value;
      summary.append(dt, dd);
    }
    quoteForm.hidden = true;
    $("#quote-review").hidden = false;
    $("#edit-quote").focus();
  });
  $("#edit-quote").addEventListener("click", () => {
    $("#quote-review").hidden = true;
    quoteForm.hidden = false;
    $("[name=need]", quoteForm).focus();
  });
  $("#preview-lead").addEventListener("click", () => {
    $("#quote-review").hidden = true;
    $("#quote-preview").hidden = false;
  });
  function resetQuote() {
    quoteForm.reset();
    contact.type = "tel";
    quoteForm.hidden = false;
    $("#quote-review").hidden = true;
    $("#quote-preview").hidden = true;
    $("#quote-summary").replaceChildren();
  }

  function wireTabs(attribute, panelPrefix) {
    const buttons = $$(`[data-${attribute}]`);
    const activate = (button) => {
      buttons.forEach((b) => {
        const active = b === button;
        b.setAttribute("aria-selected", String(active));
        b.tabIndex = active ? 0 : -1;
        $(`#${panelPrefix}-${b.dataset[attribute]}`).hidden = !active;
      });
    };
    buttons.forEach((button, index) => {
      button.addEventListener("click", () => activate(button));
      button.addEventListener("keydown", (e) => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) return;
        e.preventDefault();
        const next =
          e.key === "Home"
            ? 0
            : e.key === "End"
              ? buttons.length - 1
              : (index + (e.key === "ArrowRight" ? 1 : -1) + buttons.length) %
                buttons.length;
        activate(buttons[next]);
        buttons[next].focus();
      });
    });
  }
  wireTabs("stage", "stage");
  wireTabs("manage", "manage");
  $("#preview-claim").addEventListener("click", () => {
    $("#claim-pending").hidden = false;
  });
  $("#profile-preview").addEventListener("submit", (e) => {
    e.preventDefault();
    $("#profile-saved").hidden = false;
  });
  $("#lead-toggle").addEventListener("click", (e) => {
    const button = e.currentTarget;
    $("#lead-detail").hidden = !$("#lead-detail").hidden;
    button.setAttribute("aria-expanded", String(!$("#lead-detail").hidden));
  });
})();
