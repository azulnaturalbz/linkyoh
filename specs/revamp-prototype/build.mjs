import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.dirname(fileURLToPath(import.meta.url));
const esc = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const icon = (name) => `<i data-lucide="${name}" aria-hidden="true"></i>`;
const copy = {
  en: {
    notice: "Design preview · Fictional businesses & checks · Nothing is sent",
    skip: "Skip to content",
    discover: "Find services",
    pros: "Linkyoh for Pros",
    menu: "Menu",
    close: "Close",
    language: "Language",
    country: "LOCAL SERVICES, BELIZE",
    ask: "What do you need done?",
    intro: "Find the right people. Know what’s checked. Get in touch.",
    placeholder: "A plumber in Cayo, a carpenter in Belmopan…",
    find: "Find a pro",
    examples: "Try a need",
    example1: "Plumber in Cayo",
    example2: "Carpenter in Belmopan",
    classic: "Browse by category or area",
    category: "Service",
    district: "District",
    town: "Town or village",
    allServices: "All services",
    allDistricts: "All districts",
    allTowns: "All towns",
    plumbing: "Plumbing",
    carpentry: "Carpentry",
    apply: "Apply filters",
    clear: "Clear filters",
    nearby: "People for your next project",
    all: "Explore all services",
    nearbySub: "From everyday fixes to something made just for you.",
    checked: "Checked",
    phone: "Phone confirmed",
    claimed: "Owner claimed",
    notClaimed: "Owner not claimed",
    unknown: "Not yet verified",
    verified: "Verified",
    checkDate: "Check date unknown",
    scopeUnknown: "Verification scope unknown",
    seeChecks: "See what’s checked",
    pricing: "Ask for a quote",
    profile: "View provider",
    areas: "Service areas",
    availability: "Availability not confirmed",
    results: "Find your match",
    resultSub: "Local people, with the details that matter.",
    resultCount: "providers",
    relevance: "Sorted by service and area match",
    filter: "Filters",
    matched: "Your search",
    empty: "No matching providers yet",
    emptySub: "Try another service or a wider area. We won’t invent a match.",
    urgent:
      "Need someone tonight? Confirm availability directly with the provider.",
    back: "All services",
    photos: "Work photos",
    photoNote: "Illustrative photos · Not evidence of completed work",
    about: "About this provider",
    whatDo: "What we do",
    whatDont: "What we don’t do",
    unknownLimits:
      "Service exclusions have not been supplied. Ask the provider.",
    coverage: "Area coverage is not a promise of availability.",
    contact: "Let’s talk about your project",
    whatsapp: "Contact on WhatsApp",
    quote: "Request a quote",
    contactSub: "Share what you need, then agree the details directly.",
    source: "Sample profile · No real business or contact information",
    correction: "Suggest a correction",
    own: "Is this your business?",
    claim: "Claim this profile",
    manageProfile: "Manage this profile",
    ownership:
      "A claimed profile has a confirmed owner. Checks describe their scope, not a guarantee of work.",
    maker: "Sell what you make.",
    forward: "Open your own store on MarketDay",
    powered: "Powered by Silvatech™",
    footerTag: "Local expertise. Connected by Silvatech.",
    photo: "Photo",
    next: "Next photo",
    previous: "Previous photo",
    quoteTitle: "Request a quote",
    need: "What needs doing?",
    needPlaceholder: "Tell the provider about the job…",
    contactMethod: "How can the provider contact you?",
    contactDetails: "Your phone or email",
    whatsappOption: "WhatsApp",
    email: "Email",
    consent:
      "I agree to share this request and my contact details with this provider through WOP.",
    review: "Review request",
    summary: "Review your request",
    notSent: "Preview only. Your request has not been sent.",
    edit: "Edit request",
    previewLead: "Preview lead status",
    leadPreview: "WOP lead preview",
    awaiting: "Awaiting provider response",
    previewOnly: "Sample state only · No lead created",
    notification: "WhatsApp notification",
    notificationPending: "Delivery not attempted",
    directTitle: "WhatsApp contact preview",
    directBody:
      "This is a fictional provider with no phone number. No WhatsApp conversation has been opened.",
    correctTitle: "Suggest a correction",
    correctBody:
      "The live flow will let you report inaccurate public details for review. This sample does not submit a report.",
    proHeading: "Your work. Your profile.",
    proSub:
      "Free verified provider profile. Verification is subject to review.",
    claimStage: "Claim",
    verifyStage: "Verify",
    manageStage: "Manage",
    claimTitle: "Make this profile yours",
    claimBody:
      "Confirm the business you represent, sign in, and submit ownership evidence for review.",
    claimButton: "Preview claim review",
    pending: "Claim pending review",
    pendingBody:
      "Only an authorized reviewer can approve ownership. No account or claim is created here.",
    verifyTitle: "Make every check count",
    verifyBody:
      "Phone, ownership and verification dates stay separate. A missing check stays unknown.",
    phonePending: "Phone check pending",
    ownerPending: "Ownership evidence under review",
    dashboard: "Provider dashboard",
    profileTab: "Profile",
    inboxTab: "Leads inbox",
    editTitle: "Public profile",
    businessName: "Business name",
    description: "What you do",
    save: "Preview changes",
    saved: "Preview updated. Nothing has been saved.",
    inboxTitle: "Quote requests",
    leadNeed: "Leaking kitchen tap",
    leadArea: "San Ignacio, Cayo",
    leadStatus: "Awaiting reply",
    consented: "Contact sharing consent recorded",
    leadDetail: "Request details",
    noContact: "Contact details omitted from this sample.",
    notifications: "WhatsApp on quote requests",
    notifyHint: "Requires owner opt-in and reviewed WOP delivery.",
    checkTitle: "What “Checked” means",
    notGuarantee:
      "A check is limited to the scope and date shown. It is not proof of licensing, insurance or workmanship.",
    allUnknown: "No verification evidence recorded.",
    introProvider: "Residential repairs and practical work for your home.",
    plumbingDesc:
      "Help with leaking taps, sink fittings and small residential plumbing repairs. Discuss the job and a quote before work starts.",
    carpentryDesc:
      "Custom shelves, cabinets and practical woodwork for homes. Discuss measurements, materials and a quote with the maker.",
    repairs: [
      "Tap and sink repairs",
      "Fixture installation",
      "Small residential pipe repairs",
    ],
    limits: ["Major sewer excavation", "Gas appliance work"],
    woodwork: [
      "Custom shelving",
      "Cabinet repairs",
      "Made-to-measure furniture",
    ],
    woodLimits: ["Structural engineering", "Electrical installation"],
  },
  es: {
    notice:
      "Vista de diseño · Negocios y verificaciones ficticios · Sin envíos",
    skip: "Ir al contenido",
    discover: "Buscar servicios",
    pros: "Linkyoh para profesionales",
    menu: "Menú",
    close: "Cerrar",
    language: "Idioma",
    country: "SERVICIOS LOCALES, BELICE",
    ask: "¿Qué necesitas resolver?",
    intro:
      "Encuentra a la persona indicada. Revisa sus verificaciones. Contáctala.",
    placeholder: "Un plomero en Cayo, un carpintero en Belmopán…",
    find: "Buscar",
    examples: "Busca lo que necesitas",
    example1: "Plomero en Cayo",
    example2: "Carpintero en Belmopán",
    classic: "Explorar por categoría o zona",
    category: "Servicio",
    district: "Distrito",
    town: "Ciudad o pueblo",
    allServices: "Todos los servicios",
    allDistricts: "Todos los distritos",
    allTowns: "Todas las localidades",
    plumbing: "Plomería",
    carpentry: "Carpintería",
    apply: "Aplicar filtros",
    clear: "Quitar filtros",
    nearby: "Personas para tu próximo proyecto",
    all: "Explorar todos los servicios",
    nearbySub: "Desde reparaciones cotidianas hasta algo hecho para ti.",
    checked: "Comprobado",
    phone: "Teléfono confirmado",
    claimed: "Titularidad confirmada",
    notClaimed: "Sin titular confirmado",
    unknown: "Aún sin verificar",
    verified: "Verificado",
    checkDate: "Fecha de revisión desconocida",
    scopeUnknown: "Alcance de verificación desconocido",
    seeChecks: "Ver las comprobaciones",
    pricing: "Solicita una cotización",
    profile: "Ver proveedor",
    areas: "Zonas de servicio",
    availability: "Disponibilidad sin confirmar",
    results: "Encuentra a tu profesional",
    resultSub: "Personas de tu zona, con los detalles que importan.",
    resultCount: "proveedores",
    relevance: "Ordenados por servicio y zona",
    filter: "Filtros",
    matched: "Tu búsqueda",
    empty: "Aún no hay proveedores que coincidan",
    emptySub:
      "Prueba otro servicio o una zona más amplia. No inventaremos resultados.",
    urgent:
      "¿Lo necesitas esta noche? Confirma la disponibilidad con el proveedor.",
    back: "Todos los servicios",
    photos: "Fotos del trabajo",
    photoNote: "Fotos ilustrativas · No acreditan trabajos realizados",
    about: "Sobre este proveedor",
    whatDo: "Lo que hacemos",
    whatDont: "Lo que no hacemos",
    unknownLimits:
      "No se han indicado exclusiones del servicio. Consulta al proveedor.",
    coverage: "La cobertura de una zona no garantiza disponibilidad.",
    contact: "Hablemos de tu proyecto",
    whatsapp: "Contactar por WhatsApp",
    quote: "Solicitar cotización",
    contactSub: "Cuéntanos qué necesitas y acuerda los detalles directamente.",
    source: "Perfil de ejemplo · Sin datos reales de negocio o contacto",
    correction: "Sugerir una corrección",
    own: "¿Es tu negocio?",
    claim: "Reclamar este perfil",
    manageProfile: "Gestionar este perfil",
    ownership:
      "Un perfil reclamado tiene un titular confirmado. Las comprobaciones no garantizan el trabajo.",
    maker: "Vende lo que creas.",
    forward: "Abre tu propia tienda en MarketDay",
    powered: "Tecnología de Silvatech™",
    footerTag: "Experiencia local. Conectada por Silvatech.",
    photo: "Foto",
    next: "Siguiente foto",
    previous: "Foto anterior",
    quoteTitle: "Solicitar cotización",
    need: "¿Qué trabajo necesitas?",
    needPlaceholder: "Describe el trabajo al proveedor…",
    contactMethod: "¿Cómo puede contactarte el proveedor?",
    contactDetails: "Tu teléfono o correo",
    whatsappOption: "WhatsApp",
    email: "Correo electrónico",
    consent:
      "Acepto compartir esta solicitud y mis datos de contacto con este proveedor a través de WOP.",
    review: "Revisar solicitud",
    summary: "Revisa tu solicitud",
    notSent: "Solo una vista previa. Tu solicitud no se ha enviado.",
    edit: "Editar solicitud",
    previewLead: "Ver estado de ejemplo",
    leadPreview: "Vista previa del contacto en WOP",
    awaiting: "Pendiente de respuesta del proveedor",
    previewOnly: "Estado de ejemplo · No se creó un contacto",
    notification: "Aviso por WhatsApp",
    notificationPending: "Sin intento de envío",
    directTitle: "Vista previa de contacto por WhatsApp",
    directBody:
      "Este proveedor es ficticio y no tiene número de teléfono. No se ha abierto ninguna conversación.",
    correctTitle: "Sugerir una corrección",
    correctBody:
      "El servicio permitirá reportar datos públicos incorrectos para revisión. Este ejemplo no envía reportes.",
    proHeading: "Tu trabajo. Tu perfil.",
    proSub:
      "Perfil verificado gratuito. La verificación está sujeta a revisión.",
    claimStage: "Reclamar",
    verifyStage: "Verificar",
    manageStage: "Gestionar",
    claimTitle: "Haz tuyo este perfil",
    claimBody:
      "Confirma el negocio que representas, inicia sesión y presenta pruebas de titularidad para revisión.",
    claimButton: "Ver revisión de ejemplo",
    pending: "Reclamación pendiente de revisión",
    pendingBody:
      "Solo un revisor autorizado puede aprobar la titularidad. Aquí no se crea una cuenta ni una reclamación.",
    verifyTitle: "Cada comprobación importa",
    verifyBody:
      "El teléfono, la titularidad y las fechas se comprueban por separado. Lo desconocido sigue sin confirmar.",
    phonePending: "Teléfono pendiente de revisión",
    ownerPending: "Prueba de titularidad en revisión",
    dashboard: "Panel del proveedor",
    profileTab: "Perfil",
    inboxTab: "Solicitudes",
    editTitle: "Perfil público",
    businessName: "Nombre del negocio",
    description: "Tus servicios",
    save: "Ver cambios",
    saved: "Vista previa actualizada. No se guardó ningún cambio.",
    inboxTitle: "Solicitudes de cotización",
    leadNeed: "Grifo de cocina con fuga",
    leadArea: "San Ignacio, Cayo",
    leadStatus: "Pendiente de respuesta",
    consented: "Consentimiento para compartir contacto registrado",
    leadDetail: "Detalles de la solicitud",
    noContact: "Datos de contacto omitidos en este ejemplo.",
    notifications: "WhatsApp al recibir cotizaciones",
    notifyHint: "Requiere autorización del titular y un envío de WOP revisado.",
    checkTitle: "Qué significa «Comprobado»",
    notGuarantee:
      "La comprobación se limita al alcance y la fecha indicados. No acredita licencias, seguros ni calidad del trabajo.",
    allUnknown: "Sin pruebas de verificación registradas.",
    introProvider: "Reparaciones y trabajos prácticos para tu hogar.",
    plumbingDesc:
      "Ayuda con grifos que gotean, conexiones de fregaderos y reparaciones pequeñas de plomería residencial. Acuerda el trabajo y la cotización antes de comenzar.",
    carpentryDesc:
      "Estantes, gabinetes y trabajos de madera a medida para el hogar. Acuerda las medidas, los materiales y la cotización con el fabricante.",
    repairs: [
      "Reparación de grifos y fregaderos",
      "Instalación de accesorios",
      "Reparaciones pequeñas de tuberías",
    ],
    limits: [
      "Excavaciones mayores de alcantarillado",
      "Trabajos con aparatos de gas",
    ],
    woodwork: [
      "Estantes a medida",
      "Reparación de gabinetes",
      "Muebles personalizados",
    ],
    woodLimits: ["Ingeniería estructural", "Instalaciones eléctricas"],
  },
};

// Fictional, isolated design records. These are not claims about real providers.
const providers = [
  {
    id: "riverbend",
    name: "Riverbend Plumbing",
    category: "plumbing",
    district: "Cayo",
    towns: ["San Ignacio", "Santa Elena"],
    image: "plumbing.png",
    photos: ["plumbing.png"],
    checks: [
      { scope: "phone", date: "2026-08-12" },
      { scope: "claimed", date: "2026-08-12" },
    ],
    verified: "2026-08-12",
    maker: false,
  },
  {
    id: "pine",
    name: "Pine & Plane Studio",
    category: "carpentry",
    district: "Cayo",
    towns: ["Belmopan", "San Ignacio"],
    image: "workshop.jpg",
    photos: ["workshop.jpg", "workbench.jpg"],
    checks: [{ scope: "phone", date: "2026-08-19" }],
    verified: null,
    maker: true,
  },
  {
    id: "west",
    name: "Westside Home Repairs",
    category: "plumbing",
    district: "Cayo",
    towns: ["Belmopan"],
    image: "pipe-repair.png",
    photos: ["pipe-repair.png"],
    checks: [],
    verified: null,
    maker: false,
  },
];
const towns = {
  Cayo: ["San Ignacio", "Santa Elena", "Belmopan"],
  Belize: ["Belize City", "Ladyville"],
  Corozal: ["Corozal Town"],
  "Orange Walk": ["Orange Walk Town"],
  "Stann Creek": ["Dangriga", "Hopkins"],
  Toledo: ["Punta Gorda"],
};
const profileFile = (p) =>
  p.id === "riverbend" ? "provider.html" : `provider-${p.id}.html`;
const ecosystem = [
  ["hub", "Silvatech", "https://silvatech.bz/"],
  ["visitbelize", "Visit Belize", "https://visitbelize.silvatech.bz/"],
  ["chillbout", "Chillbout", null],
  ["linkyoh", "Linkyoh", "https://linkyoh.com/"],
  ["marketday", "MarketDay", "https://marketday.silvatech.bz/"],
  ["wop", "WOP", "https://wop.silvatech.bz/"],
  ["payments", "Payments", "https://payments.silvatech.bz/"],
  ["consulta", "Consulta", "https://consulta.silvatech.bz/"],
  ["logistics", "Belize Logistics", null],
];
const ecoURL = (url, campaign) =>
  `${url}?utm_source=linkyoh&utm_medium=ecosystem&utm_campaign=${campaign}`;
const forward = (c) =>
  `<aside class="forward"><div>${icon("store")}<p><strong>${c.maker}</strong> <a href="${ecoURL("https://marketday.silvatech.bz/", "forward")}" data-track="marketday_clickout" rel="noreferrer">${c.forward} ${icon("arrow-up-right")}</a></p></div></aside>`;
function checked(p, c) {
  return `<div class="checked ${p.checks.length ? "" : "checked--unknown"}"><div class="checked-title">${icon(p.checks.length ? "badge-check" : "badge-help")}<strong>${c.checked}</strong>${p.verified ? `<span>${c.verified} <time datetime="${p.verified}">${p.verified}</time></span>` : `<span>${c.unknown}</span>`}</div><div class="check-scopes">${p.checks.length ? p.checks.map((x) => `<span>${esc(c[x.scope])}<time datetime="${x.date}">${x.date}</time></span>`).join("") : `<span>${c.scopeUnknown}</span><span>${c.checkDate}</span>`}${!p.checks.some((x) => x.scope === "claimed") ? `<span>${c.notClaimed}</span>` : ""}</div></div>`;
}
function card(p, c, prefix) {
  return `<article class="provider-card" data-provider="${p.id}" data-category="${p.category}" data-district="${p.district}" data-towns="${esc(p.towns.join("|"))}"><a class="card-image" href="${profileFile(p)}" aria-label="${esc(p.name)}"><img src="${prefix}assets/${p.image}" alt="${esc(c[p.category])}" width="600" height="400"><span class="photo-label">${c[p.category]}</span></a><div class="card-body"><div class="card-location">${icon("map-pin")} ${p.towns[0]}, ${p.district}</div><h3><a href="${profileFile(p)}">${esc(p.name)}</a></h3>${checked(p, c)}<p class="card-services">${p.category === "plumbing" ? c.repairs.slice(0, 2).join(" · ") : c.woodwork.slice(0, 2).join(" · ")}</p><div class="card-bottom"><span>${c.pricing}</span><a class="card-link" href="${profileFile(p)}" aria-label="${c.profile}: ${esc(p.name)}">${c.profile}${icon("arrow-right")}</a></div></div></article>`;
}
function filters(c, id, open = false) {
  return `<details class="filters" ${open ? "open" : ""}><summary>${icon("sliders-horizontal")}<span>${open ? c.filter : c.classic}</span>${icon("chevron-down")}</summary><div class="filter-fields"><label for="category-${id}">${c.category}<select name="category" id="category-${id}"><option value="">${c.allServices}</option><option value="plumbing">${c.plumbing}</option><option value="carpentry">${c.carpentry}</option></select></label><label for="district-${id}">${c.district}<select name="district" id="district-${id}"><option value="">${c.allDistricts}</option>${Object.keys(
    towns,
  )
    .map((d) => `<option>${d}</option>`)
    .join(
      "",
    )}</select></label><label for="town-${id}">${c.town}<select name="town" id="town-${id}"><option value="">${c.allTowns}</option>${Object.values(
    towns,
  )
    .flat()
    .map((t) => `<option>${t}</option>`)
    .join(
      "",
    )}</select></label><button class="btn filter-apply" type="submit">${icon("search")}${c.apply}</button></div></details>`;
}
function search(c, home = false) {
  return `<form class="search-form ${home ? "home-search" : ""}" action="results.html" method="get"><label ${home ? 'class="sr-only"' : ""} for="need">${c.ask}</label><div class="search-input">${icon("search")}<input type="search" id="need" name="q" placeholder="${c.placeholder}" maxlength="200"><button class="btn btn-primary" type="submit">${c.find}${icon("arrow-right")}</button></div>${filters(c, home ? "home" : "results", !home)}</form>`;
}
function home(c, prefix) {
  return `<section class="discovery-head wrap"><p class="eyebrow">${icon("map-pin")}${c.country}</p><h1>${c.ask}</h1><p class="intro">${c.intro}</p>${search(c, true)}<div class="examples"><span>${c.examples}</span><a href="results.html?q=${encodeURIComponent(c.example1)}">${c.example1}${icon("arrow-up-right")}</a><a href="results.html?q=${encodeURIComponent(c.example2)}">${c.example2}${icon("arrow-up-right")}</a></div></section><section class="discover-band"><div class="wrap"><div class="section-heading"><div><h2>${c.nearby}</h2><p>${c.nearbySub}</p></div><a class="text-link" href="results.html">${c.all}${icon("arrow-right")}</a></div><div class="card-grid">${providers.map((p) => card(p, c, prefix)).join("")}</div></div></section><div class="wrap">${forward(c)}<section class="pros-band"><div><span class="eyebrow">${c.pros}</span><h2>${c.proHeading}</h2><p>${c.proSub}</p></div><button class="btn btn-primary" data-open="pros">${c.claim}${icon("arrow-right")}</button></section></div>`;
}
function results(c, prefix) {
  return `<section class="results-head wrap"><p class="eyebrow">${icon("map-pin")}${c.country}</p><h1>${c.results}</h1><p class="intro">${c.resultSub}</p>${search(c)}</section><section class="discover-band"><div class="wrap"><div id="search-context" class="search-context" hidden></div><p id="urgency" class="notice" hidden>${icon("clock-3")}${c.urgent}</p><div class="section-heading result-heading"><h2><span id="result-count">3</span> ${c.resultCount}</h2><span class="muted">${c.relevance}</span></div><div class="card-grid" id="results-grid">${providers.map((p) => card(p, c, prefix)).join("")}</div><div class="empty" id="empty-state" hidden>${icon("search-x")}<h2>${c.empty}</h2><p>${c.emptySub}</p><a class="btn btn-primary" href="results.html">${c.clear}</a></div></div></section>`;
}
function provider(p, c, prefix) {
  const list = (items) =>
    `<ul class="service-list">${items.map((x) => `<li>${icon("check")}${esc(x)}</li>`).join("")}</ul>`;
  return `<div class="wrap provider-page"><a class="back-link" href="results.html">${icon("arrow-left")}${c.back}</a><div class="provider-layout"><div class="provider-main"><header class="provider-heading"><p class="eyebrow">${c[p.category]} · ${p.district}, Belize</p><h1>${esc(p.name)}</h1><p class="provider-location">${icon("map-pin")}${p.towns.join(" · ")}</p>${checked(p, c)}<button class="text-link small" data-open="checks">${c.seeChecks}${icon("info")}</button></header><div class="contact-inline">${contact(p, c)}</div><section class="photo-section"><h2>${c.photos}</h2><button class="provider-photo" data-open="photos" aria-label="${c.photos}"><img src="${prefix}assets/${p.image}" alt="${c[p.category]}" width="1200" height="800"><span>${icon("images")}${p.photos.length} ${c.photo}${p.photos.length > 1 ? "s" : ""}</span></button><p class="caption">${c.photoNote}</p></section><section class="provider-section"><h2>${c.about}</h2><p>${p.category === "plumbing" ? c.plumbingDesc : c.carpentryDesc}</p><div class="service-columns"><div><h3>${c.whatDo}</h3>${list(p.category === "plumbing" ? c.repairs : c.woodwork)}</div><div><h3>${c.whatDont}</h3>${p.id === "west" ? `<p>${c.unknownLimits}</p>` : list(p.maker ? c.woodLimits : c.limits)}</div></div></section><section class="provider-section"><h2>${c.areas}</h2><div class="area-list">${p.towns.map((t) => `<span>${icon("map-pin")}${t}, ${p.district}</span>`).join("")}</div><p class="muted">${c.coverage}</p></section>${p.maker ? forward(c) : ""}<p class="source-line">${c.source}</p><button class="text-link" data-open="correction">${c.correction}${icon("flag")}</button></div><aside class="provider-sidebar"><div class="desktop-contact">${contact(p, c)}</div><section class="claim-block"><h2>${c.own}</h2><p>${c.ownership}</p><button class="btn secondary" data-open="pros" ${p.checks.some(check => check.scope === "claimed") ? 'data-start="manage"' : ""}>${icon("key-round")}${p.checks.some(check => check.scope === "claimed") ? c.manageProfile : c.claim}</button></section>${!p.maker ? forward(c) : ""}</aside></div></div>`;
}
function contact(p, c) {
  return `<section class="contact-panel"><h2>${c.contact}</h2><p>${c.contactSub}</p><button class="svt-whatsapp" data-open="whatsapp">${icon("message-circle")}${c.whatsapp}</button><button class="btn secondary" data-open="quote">${icon("file-text")}${c.quote}</button><div class="availability">${icon("clock-3")}${c.availability}</div></section>`;
}
function dialogs(c, p, prefix) {
  const claimRecord = p.checks.find(check => check.scope === "claimed");
  const pro = claimRecord ? {
    ...c, claimTitle: c.claimed, claimBody: c.ownership, claimButton: c.seeChecks,
    pending: c.claimed, pendingBody: `${claimRecord.date} · ${c.notice}`,
  } : c;
  const dialog = (id, title, body, cls = "") =>
    `<dialog id="${id}" class="modal ${cls}" aria-labelledby="${id}-title"><div class="modal-top"><h2 id="${id}-title">${title}</h2><button class="icon-button" data-close aria-label="${c.close}" title="${c.close}">${icon("x")}</button></div>${body}</dialog>`;
  return (
    dialog(
      "whatsapp",
      c.directTitle,
      `<p>${c.directBody}</p><button class="btn btn-primary" data-close>${c.close}</button>`,
    ) +
    dialog(
      "correction",
      c.correctTitle,
      `<p>${c.correctBody}</p><button class="btn btn-primary" data-close>${c.close}</button>`,
    ) +
    dialog(
      "checks",
      c.checkTitle,
      `${checked(p, c)}<p>${c.notGuarantee}</p><p class="notice">${c.notice}</p>`,
    ) +
    dialog(
      "photos",
      c.photos,
      `<img id="gallery-image" src="${prefix}assets/${p.photos[0]}" alt="${c[p.category]}" width="1200" height="800"><div class="gallery-actions"><button class="icon-button" data-photo="-1" title="${c.previous}" aria-label="${c.previous}" ${p.photos.length === 1 ? "disabled" : ""}>${icon("arrow-left")}</button><span id="photo-count">1 / ${p.photos.length}</span><button class="icon-button" data-photo="1" title="${c.next}" aria-label="${c.next}" ${p.photos.length === 1 ? "disabled" : ""}>${icon("arrow-right")}</button></div><p class="caption">${c.photoNote}</p>`,
      "gallery",
    ) +
    dialog(
      "quote",
      c.quoteTitle,
      `<p class="recipient">${icon("user-round")}${p.name}</p><p class="notice">${c.notSent}</p><form id="quote-form"><label>${c.need}<textarea name="need" rows="3" maxlength="1000" required placeholder="${c.needPlaceholder}"></textarea></label><label>${c.town}<select name="area" required>${p.towns.map((t) => `<option>${t}, ${p.district}</option>`).join("")}</select></label><label>${c.contactMethod}<select name="method"><option value="whatsapp">${c.whatsappOption}</option><option value="email">${c.email}</option></select></label><label>${c.contactDetails}<input name="contact" type="tel" autocomplete="off" maxlength="100" required></label><label class="checkbox"><input type="checkbox" name="consent" required><span>${c.consent}</span></label><button class="btn btn-primary" type="submit">${c.review}${icon("arrow-right")}</button></form><section id="quote-review" hidden><h3>${c.summary}</h3><dl id="quote-summary"></dl><button class="btn secondary" id="edit-quote">${c.edit}</button><button class="btn btn-primary" id="preview-lead">${c.previewLead}</button></section><section id="quote-preview" hidden><div class="state-icon">${icon("inbox")}</div><h3>${c.awaiting}</h3><p>${c.previewOnly}</p><p>${c.notification}: <strong>${c.notificationPending}</strong></p></section>`,
    ) +
    dialog(
      "pros",
      c.pros,
      `<div class="pros-intro"><h3>${c.proHeading}</h3><p>${c.proSub}</p></div><div class="stage-tabs" role="tablist" aria-label="${c.pros}">${["claim", "verify", "manage"].map((s, i) => `<button role="tab" id="tab-${s}" aria-selected="${i === 0}" aria-controls="stage-${s}" data-stage="${s}" tabindex="${i === 0 ? "0" : "-1"}"><span>${i + 1}</span>${c[`${s}Stage`]}</button>`).join("")}</div><section role="tabpanel" id="stage-claim" aria-labelledby="tab-claim"><h3>${pro.claimTitle}</h3><p>${pro.claimBody}</p><div class="provider-row">${icon("briefcase-business")}<div><strong>${p.name}</strong><span>${p.district}, Belize</span></div></div><button class="btn btn-primary" id="preview-claim">${pro.claimButton}${icon("arrow-right")}</button><div id="claim-pending" class="notice" hidden><strong>${pro.pending}</strong><p>${pro.pendingBody}</p></div></section><section role="tabpanel" id="stage-verify" aria-labelledby="tab-verify" hidden><h3>${c.verifyTitle}</h3><p>${c.verifyBody}</p>${p.checks.length ? checked(p,c) : `<ul class="verification-list"><li>${icon("phone")}<span>${c.phonePending}</span>${icon("clock-3")}</li><li>${icon("file-check-2")}<span>${c.ownerPending}</span>${icon("clock-3")}</li></ul>`}<p class="muted">${c.notGuarantee}</p></section><section role="tabpanel" id="stage-manage" aria-labelledby="tab-manage" hidden><h3>${c.dashboard}</h3><div class="dashboard-tabs" role="tablist" aria-label="${c.dashboard}"><button role="tab" id="tab-profile" aria-selected="true" aria-controls="manage-profile" data-manage="profile">${icon("store")}${c.profileTab}</button><button role="tab" id="tab-inbox" aria-selected="false" aria-controls="manage-inbox" data-manage="inbox" tabindex="-1">${icon("inbox")}${c.inboxTab}<span class="count">1</span></button></div><section role="tabpanel" id="manage-profile" aria-labelledby="tab-profile"><form id="profile-preview"><label>${c.businessName}<input value="${p.name}" required maxlength="100"></label><label>${c.description}<textarea rows="3" required maxlength="500">${p.category === "plumbing" ? c.plumbingDesc : c.carpentryDesc}</textarea></label><button class="btn btn-primary" type="submit">${c.save}</button><p id="profile-saved" role="status" hidden>${c.saved}</p></form></section><section role="tabpanel" id="manage-inbox" aria-labelledby="tab-inbox" hidden><p class="notice">${c.previewOnly}</p><button class="lead-item" id="lead-toggle" aria-expanded="false" aria-controls="lead-detail"><span>${icon("message-square-text")}<strong>${c.leadNeed}</strong></span><span>${c.leadArea}</span><span class="status-chip">${c.leadStatus}</span>${icon("chevron-down")}</button><div id="lead-detail" class="lead-detail" hidden><h4>${c.leadDetail}</h4><p>${c.consented}</p><p>${c.noContact}</p><p>${c.notification}: ${c.notificationPending}</p></div><label class="checkbox"><input type="checkbox" id="notify-opt-in"><span>${c.notifications}</span></label><p class="muted small">${c.notifyHint}</p></section></section>`,
      "pros-modal",
    )
  );
}
function page(lang, type, p = providers[0]) {
  const c = copy[lang],
    prefix = lang === "es" ? "../" : "",
    filename =
      type === "home"
        ? "index.html"
        : type === "results"
          ? "results.html"
          : profileFile(p);
  const content =
    type === "home"
      ? home(c, prefix)
      : type === "results"
        ? results(c, prefix)
        : provider(p, c, prefix);
  const data = { c, providers, towns, provider: p, lang, prefix, type };
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; form-action 'self'; base-uri 'none'; object-src 'none'"><title>${type === "home" ? c.ask : type === "results" ? c.results : p.name} | Linkyoh prototype</title><link rel="stylesheet" href="${prefix}assets/silvatech-ui.css"><link rel="stylesheet" href="${prefix}prototype.css"><link rel="icon" href="data:,"></head><body data-page="${type}"><a class="skip-link" href="#main">${c.skip}</a><div class="preview-notice">${c.notice}</div><header class="site-header"><div class="wrap nav-inner"><a class="wordmark" href="index.html">linkyoh<span>™</span><span class="wordmark-dot" aria-hidden="true">.</span></a><nav class="desktop-nav" aria-label="${c.menu}"><a href="results.html">${c.discover}</a><button class="text-link" data-open="pros">${c.pros}${icon("arrow-up-right")}</button></nav><div class="nav-tools"><nav class="language-switch" aria-label="${c.language}"><a href="${lang === "es" ? "../" : ""}${filename}" lang="en" hreflang="en" ${lang === "en" ? 'aria-current="true"' : ""}>EN</a><a href="${lang === "es" ? "" : "es/"}${filename}" lang="es" hreflang="es" ${lang === "es" ? 'aria-current="true"' : ""}>ES</a></nav><button class="icon-button menu-button" aria-label="${c.menu}" title="${c.menu}" aria-expanded="false" aria-controls="mobile-menu" id="menu-toggle">${icon("menu")}</button></div></div><nav id="mobile-menu" hidden aria-label="${c.menu}"><a href="results.html">${c.discover}</a><button class="text-link" data-open="pros">${c.pros}</button></nav></header><main id="main">${content}</main><footer><div class="wrap footer-intro"><a class="wordmark" href="index.html">linkyoh<span>™</span></a><span>${c.footerTag}</span></div><nav class="svt-ecosystem-strip" aria-label="Silvatech ecosystem"><ul>${ecosystem.map(([key, label, url]) => `<li>${url ? `<a href="${ecoURL(url, "strip")}" data-track="${key}_clickout" rel="noreferrer">${label}</a>` : `<span class="svt-ecosystem-strip__inactive">${label}</span>`}</li>`).join("")}</ul></nav><div class="legal wrap"><a href="${ecoURL("https://silvatech.bz/", "powered_by")}" data-track="hub_clickout" rel="noreferrer">${c.powered}${icon("arrow-up-right")}</a><p>© 2026 Silvatech™. Silvatech, WOP, MarketDay, Linkyoh, Chillbout, Visit Belize and Belize Logistics are trademarks of Silvatech, Belize City, Belize.</p></div></footer>${dialogs(c, p, prefix)}<script src="${prefix}assets/lucide.min.js"></script><script src="data-${type === "provider" ? p.id : type}.js"></script><script src="${prefix}prototype.js"></script></body></html>`;
}
for (const lang of ["en", "es"]) {
  const dir = path.join(root, lang === "en" ? "" : "es");
  await mkdir(dir, { recursive: true });
  for (const [type, p] of [
    ["home", providers[0]],
    ["results", providers[0]],
    ...providers.map((p) => ["provider", p]),
  ]) {
    const filename =
      type === "home"
        ? "index.html"
        : type === "results"
          ? "results.html"
          : profileFile(p);
    await writeFile(path.join(dir, filename), page(lang, type, p));
    await writeFile(
      path.join(dir, `data-${type === "provider" ? p.id : type}.js`),
      `window.PROTOTYPE = ${JSON.stringify({ c: copy[lang], providers, towns, provider: p, lang, prefix: lang === "es" ? "../" : "", type })};\n`,
    );
  }
}
console.log(
  "Built 3 page types in EN/ES, including 2 extra fixture provider profiles per language.",
);
