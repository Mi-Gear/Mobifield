<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#111820">
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <title>Инвентарь — Mobifield</title>
  <style>
    :root {
      color-scheme:dark; --gold:#b99a68; --gold2:#806747; --text:#e5dfd2;
      --muted:#9d9a91; --common:#777b78; --rare:#638b9b; --epic:#80658f; --legendary:#b18a4e;
    }
    * { box-sizing:border-box; }
    html { min-height:100%; background:#283a4c; }
    body {
      margin:0; min-height:100vh; color:var(--text); font:14px/1.4 "Trebuchet MS",Georgia,serif;
      background:
        radial-gradient(ellipse at 50% -20%,#34302b 0,transparent 48%),
        radial-gradient(ellipse at 10% 100%,#252a27 0,transparent 42%),
        linear-gradient(145deg,#111513,#1b211e 52%,#101412);
      background-attachment:scroll;
    }
    /* Не размываем весь viewport при каждом кадре прокрутки. */
    body:before { content:""; position:absolute; inset:0 0 auto; height:100vh; z-index:-1; background:radial-gradient(ellipse at center,#a18a5b0b,transparent 68%); pointer-events:none; }
    button,input,select { font:inherit; }
    button { color:inherit; }
    .page { width:min(1500px,100%); min-height:100vh; margin:0 auto; padding:0 22px 18px; display:flex; flex-direction:column; }
    .topbar {
      min-height:58px; display:flex; align-items:center; gap:18px; margin:0 -22px 18px; padding:0 22px;
      background:linear-gradient(90deg,#171b19f5,#292a24f2 55%,#171b19f5);
      border-bottom:1px solid #8b744b88; box-shadow:0 3px 14px #0009;
    }
    .brand { display:flex; align-items:center; gap:12px; flex:0 0 auto; }
    .brand-mark { width:32px; height:32px; display:grid; place-items:center; border:1px solid #d7c59b; border-radius:7px; color:#e8d6ad; font-size:19px; background:#e8d6ad18; }
    .eyebrow { color:#f0dfb8; font:600 12px Arial,sans-serif; letter-spacing:.04em; white-space:nowrap; }
    h1 { display:none; }
    .wallet { margin-left:auto; color:#f2e4c4; font:12px Arial,sans-serif; white-space:nowrap; }
    .layout { flex:1; min-height:0; display:grid; grid-template-columns:minmax(0,1.9fr) minmax(280px,.82fr); gap:16px; align-items:stretch; }
    .inventory { min-width:0; display:flex; flex-direction:column; }
    .toolbar { display:flex; flex-direction:column; gap:0; margin-bottom:10px; }
    .tabs { display:flex; align-items:stretch; justify-content:center; gap:5px; min-height:55px; border-bottom:1px solid #8b744b88; background:linear-gradient(180deg,#282923ed,#1c201ded); padding:0 8px; }
    .tab {
      position:relative; flex:1 1 0; min-width:48px; max-width:88px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:1px;
      border:0; border-bottom:2px solid transparent; background:transparent; color:#d8dce0; padding:5px 4px;
      cursor:pointer; font:10px Arial,sans-serif; white-space:nowrap;
    }
    .tab:before { content:attr(data-symbol); display:block; font:22px/1.1 Georgia,serif; color:#d4d9dc; }
    .tab.active { color:#fff0c9; border-bottom-color:#f0d8a3; background:linear-gradient(180deg,#ffffff10,transparent); }
    .tab.active:before { color:#f4e1b7; text-shadow:0 0 9px #f1d7a0aa; }
    .search-sort { display:flex; align-items:center; gap:8px; margin:0 2px 10px; }
    .search,.sort { min-height:34px; border:1px solid #e0e1d8a0; border-radius:4px; background:#e9e7dfed; color:#3f4a53; padding:6px 10px; }
    .search { flex:1; min-width:0; }
    .sort { max-width:160px; }
    .countline { display:flex; justify-content:space-between; color:#f7f2e8; text-shadow:0 1px 3px #253747; font:11px Arial,sans-serif; margin:0 4px 8px; }
    .items { display:grid; grid-template-columns:repeat(7,minmax(0,1fr)); gap:8px; align-content:start; }
    .item { contain:layout paint; }
    .item-icon img { filter:none; }
    .item {
      position:relative; display:flex; flex-direction:column; align-items:center; justify-content:space-between;
      min-width:0; min-height:104px; aspect-ratio:.82; padding:6px 4px 5px;
      border:1px solid #766d5b; border-radius:2px; color:#e2dccd; cursor:pointer; text-align:center;
      background:linear-gradient(150deg,#45453d,#292d29);
      box-shadow:inset 0 0 0 1px #bba77a24;
    }
    .item:before { content:""; position:absolute; inset:3px; border:1px solid #ffffff6b; pointer-events:none; }
    .item:hover { border-color:#fff0c6; }
    .item.selected { outline:2px solid #fff3c9; outline-offset:1px; box-shadow:inset 0 0 0 2px #b99a5a; }
    .item.common { background:linear-gradient(150deg,#555750,#343934); }
    .item.rare { background:linear-gradient(150deg,#35545a,#23383d); }
    .item.epic { background:linear-gradient(150deg,#55405f,#34283f); }
    .item.legendary { background:linear-gradient(150deg,#6b5330,#403323); }
    .item-icon { display:grid; place-items:center; width:100%; flex:1; min-height:0; font-size:32px; }
    .item-icon img { max-width:100%; max-height:68px; object-fit:contain; filter:drop-shadow(0 2px 2px #25313a66); }
    .item-name { display:block; width:100%; color:#e3ddcf; font-size:10px; line-height:1.12; overflow-wrap:anywhere; text-shadow:0 1px #ffffff80; }
    .quantity { position:absolute; top:3px; left:4px; color:#fff; font:10px Arial,sans-serif; text-shadow:0 1px 3px #172536; }
    .detail {
      min-width:0; display:flex; flex-direction:column; align-self:start; overflow:hidden;
      border:1px solid #8b744b; border-radius:2px; background:linear-gradient(155deg,#292d29f5,#1a201df5); color:#e5dfd2;
      box-shadow:0 4px 18px #1b2d3d66;
    }
    .detail-head { padding:10px 13px; color:#fff8e8; background:linear-gradient(90deg,#51432f,#6a5738 65%,#403629); border-bottom:1px solid #a78a59; font:600 19px Georgia,serif; text-shadow:0 1px 2px #29446188; }
    .art { display:grid; place-items:center; min-height:190px; margin:0; padding:12px; background:radial-gradient(ellipse,#45473d 0,#292f2a 48%,#171d1a 100%); border-bottom:1px solid #76694f; font-size:76px; }
    .detail-image { max-width:100%; max-height:205px; object-fit:contain; filter:drop-shadow(0 5px 5px #263c4b66); }
    .rarity { padding:10px 14px 0; font:11px Arial,sans-serif; text-transform:uppercase; letter-spacing:.08em; color:#64717a; }
    .rarity.common { color:#69777e; } .rarity.rare { color:#2783a6; } .rarity.epic { color:#8554b4; } .rarity.legendary { color:#a87825; }
    h2 { margin:3px 14px 8px; color:#e8dfcb; font:600 21px Georgia,serif; }
    .description { margin:0 14px 14px; color:#bcb8ad; font:13px/1.35 Georgia,serif; white-space:pre-line; }
    .stats { margin-top:auto; padding:0 14px 12px; }
    .stat { display:flex; justify-content:space-between; gap:12px; padding:7px 0; border-top:1px solid #c9c8bd; color:#aaa69b; font:12px Arial,sans-serif; }
    .stat strong { color:#e0d7c3; font-weight:600; text-align:right; }
    .empty { grid-column:1/-1; padding:42px 12px; text-align:center; color:#fff; text-shadow:0 1px 3px #253747; border:1px dashed #ffffffa0; background:#24394b40; }
    .hint { display:none; }
    .notice { margin-top:10px; padding:8px 11px; border-left:2px solid #f0d8a3; color:#fff4d9; background:#263c526e; font:11px/1.4 Arial,sans-serif; }
    @media (min-width:851px) {
      .page { height:100vh; max-height:100vh; }
      .items { grid-template-columns:repeat(7,minmax(0,1fr)); overflow-y:auto; padding:2px 5px 12px 2px; }
      .detail { position:sticky; top:12px; }
    }
    @media (max-width:1050px) and (min-width:851px) {
      .items { grid-template-columns:repeat(5,minmax(0,1fr)); }
      .layout { grid-template-columns:minmax(0,1.45fr) minmax(260px,.9fr); }
    }
    @media (max-width:850px) {
      .page { padding:0 12px calc(16px + env(safe-area-inset-bottom)); }
      .topbar { margin:0 -12px 12px; padding:0 14px; min-height:52px; }
      .layout { grid-template-columns:minmax(0,1fr); gap:12px; }
      .items { grid-template-columns:repeat(6,minmax(0,1fr)); }
      .detail { display:grid; grid-template-columns:minmax(110px,.8fr) minmax(0,1.2fr); align-self:stretch; }
      .detail-head { grid-column:1/-1; }
      .art { grid-row:2/6; min-height:160px; }
      .rarity { padding-top:12px; }
      .description { margin-bottom:8px; }
      .stats { grid-column:1/-1; }
    }
    @media (max-width:520px) {
      .page { padding-left:8px; padding-right:8px; }
      .topbar { margin-left:-8px; margin-right:-8px; padding:0 10px; min-height:48px; gap:8px; }
      .brand-mark { width:28px; height:28px; }
      .eyebrow { font-size:11px; }
      .wallet { font-size:11px; }
      .tabs { min-height:51px; overflow-x:auto; justify-content:flex-start; scrollbar-width:none; }
      .tabs::-webkit-scrollbar { display:none; }
      .tab { flex:0 0 58px; font-size:9px; }
      .tab:before { font-size:19px; }
      .search-sort { margin:8px 0; }
      .search,.sort { min-height:38px; font-size:13px; }
      .items { grid-template-columns:repeat(4,minmax(0,1fr)); gap:5px; }
      .item { min-height:88px; aspect-ratio:.8; padding:5px 3px; }
      .item-icon img { max-height:53px; }
      .item-name { font-size:9px; }
      .quantity { font-size:9px; }
      .detail { grid-template-columns:minmax(95px,.8fr) minmax(0,1.2fr); }
      .detail-head { font-size:17px; padding:8px 10px; }
      .art { min-height:130px; padding:7px; }
      .detail-image { max-height:145px; }
      h2 { font-size:18px; margin:3px 10px 5px; }
      .rarity { padding:8px 10px 0; font-size:9px; }
      .description { margin:0 10px 8px; font-size:11px; }
      .stats { padding:0 10px 8px; }
      .stat { font-size:10px; padding:6px 0; }
    }
    /* На телефонах сведения открываются боковой выдвижной панелью,
       а не занимают место под сеткой предметов. */
    @media (max-width:850px) {
      .detail {
        position:fixed; z-index:20; top:60px; right:10px; bottom:10px;
        width:min(270px,76vw); height:auto; max-height:calc(100dvh - 80px);
        display:flex; flex-direction:column; align-self:auto; overflow-y:auto;
        overscroll-behavior:contain; box-shadow:0 8px 24px #101d2d88;
        transform:translateX(calc(100% + 20px)); visibility:hidden;
        transition:transform .24s ease,visibility .24s;
      }
      .detail.open { transform:translateX(0); visibility:visible; }
      .detail-head { display:flex; align-items:center; justify-content:space-between; gap:8px; }
      .detail-close {
        display:grid; place-items:center; flex:0 0 28px; width:28px; height:28px;
        border:1px solid #ffffff88; border-radius:50%; background:#34577988;
        color:#fff; font-size:20px; line-height:1; cursor:pointer;
      }
      .detail-head { flex:0 0 auto; }
      .art { flex:0 0 auto; min-height:150px; }
      .rarity { flex:0 0 auto; }
      h2 { flex:0 0 auto; }
      .description { flex:0 0 auto; }
      .stats { flex:0 0 auto; margin-top:auto; }
    }
    @media (max-width:360px) {
      .items { grid-template-columns:repeat(3,minmax(0,1fr)); }
      .detail { width:min(250px,78vw); top:56px; right:6px; bottom:6px; max-height:calc(100dvh - 62px); }
      .art { min-height:135px; }
    }
    @media (hover:none) { .item:hover { border-color:#e4e3d8; } .item:active { opacity:.88; } }
    .tab:focus-visible,.item:focus-visible,.sort:focus-visible,.search:focus-visible { outline:2px solid #fff0c6; outline-offset:2px; }

    /* Более сдержанный dark fantasy: меньше декора, проще поверхности и контраст. */
    :root {
      --gold:#a88b5c; --gold2:#756044; --text:#dedbd2; --muted:#96958d;
      --common:#777b78; --rare:#63818a; --epic:#796487; --legendary:#a48653;
    }
    html { background:#111310; }
    body {
      color:var(--text);
      font-family:Arial,Helvetica,sans-serif;
      background:linear-gradient(145deg,#111310,#191b17 58%,#121410);
    }
    .topbar {
      background:#191b17; border-bottom:1px solid #514936;
      box-shadow:none;
    }
    .brand-mark {
      border-color:#65563d; border-radius:4px; color:#b49a6c;
      background:#24251f; font-size:17px;
    }
    .eyebrow { color:#d0c3a7; letter-spacing:.02em; }
    .wallet { color:#c6b58e; }
    .tabs {
      min-height:48px; gap:2px; padding:0 4px;
      background:#191b17; border-bottom:1px solid #514936;
    }
    .tab {
      max-width:none; color:#aaa99f; font-size:11px;
      border-bottom:2px solid transparent;
    }
    .tab:before { color:#aaa18d; font-size:18px; }
    .tab.active {
      color:#e0d2b2; border-bottom-color:#a88b5c;
      background:#ffffff06;
    }
    .tab.active:before { color:#c5aa78; text-shadow:none; }
    .search,.sort {
      color:#dedbd2; background:#20221d; border:1px solid #454638;
      border-radius:3px;
    }
    .search::placeholder { color:#88877e; }
    .countline { color:#aaa99f; text-shadow:none; }
    .items { gap:7px; }
    .item {
      border:1px solid #42443a; border-radius:3px;
      color:#d8d5ca; background:#252720; box-shadow:none;
    }
    .item:before { display:none; }
    .item:hover { border-color:#81704d; }
    .item.selected {
      outline:1px solid #a88b5c; outline-offset:0;
      border-color:#a88b5c; box-shadow:inset 0 0 0 1px #a88b5c44;
    }
    .item.common { background:#252720; }
    .item.rare { background:#20282a; }
    .item.epic { background:#29232d; }
    .item.legendary { background:#30291f; }
    .item-icon img { filter:drop-shadow(0 2px 2px #0009); }
    .item-name { color:#d8d5ca; text-shadow:none; }
    .quantity { color:#d5cbb5; text-shadow:0 1px 2px #000; }
    .detail {
      border:1px solid #514936; border-radius:3px;
      background:#1b1d18; box-shadow:none;
    }
    .detail-head {
      color:#ded2b8; background:#25251f;
      border-bottom:1px solid #514936;
      font:600 17px Arial,Helvetica,sans-serif; text-shadow:none;
    }
    .art {
      background:#151712; border-bottom:1px solid #3e4035;
    }
    .detail-image { filter:drop-shadow(0 4px 5px #000b); }
    .rarity { color:#96958d; }
    .rarity.common { color:#96958d; }
    .rarity.rare { color:#7eabb4; }
    .rarity.epic { color:#aa8cbd; }
    .rarity.legendary { color:#c3a16a; }
    h2 { color:#e0d8c7; font-family:Georgia,serif; }
    .description { color:#b3b0a6; }
    .stat { border-top:1px solid #37392f; color:#99988e; }
    .stat strong { color:#d5cbb5; }
    .empty {
      color:#aaa99f; text-shadow:none; border:1px dashed #494a3e;
      background:#1b1d18;
    }
    .notice {
      border-left:2px solid #8e764d; color:#bdb29a; background:#1b1d18;
    }
    @media (max-width:850px) {
      .detail { box-shadow:-8px 0 24px #0008; }
      .detail-close { border:1px solid #5b594c; border-radius:3px; background:#303128; color:#ddd5c3; }
    }
    .tab:focus-visible,.item:focus-visible,.sort:focus-visible,.search:focus-visible {
      outline:2px solid #b49a6c; outline-offset:2px;
    }
  </style>
</head>
<body>
  <main class="page">
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">♜</span>
        <div class="eyebrow">Инвентарь</div>
      </div>
      <div class="wallet">◈ <span id="gold">—</span> золота</div>
    </header>

    <div class="layout">
      <section class="inventory" aria-label="Список предметов">
        <div class="toolbar">
          <nav class="tabs" id="tabs" aria-label="Фильтр по локациям">
            <button class="tab active" data-filter="all" data-symbol="✧">Все</button>
          </nav>
          <div class="search-sort">
            <input class="search" id="search" type="search" placeholder="Найти предмет…" aria-label="Поиск предметов">
            <select class="sort" id="sort" aria-label="Сортировка">
              <option value="name">По названию</option>
              <option value="rarity">По редкости</option>
              <option value="count">По количеству</option>
            </select>
          </div>
        </div>
        <div class="countline"><span>ПРЕДМЕТЫ</span><span id="total">0 предметов</span></div>
        <div class="items" id="items"><div class="empty">Загружаем содержимое сумки…</div></div>
      </section>

      <aside class="detail" id="detail" aria-live="polite">
        <div class="detail-head">Выберите предмет</div>
        <div class="art">◇</div>
        <div class="rarity">Предмет не выбран</div>
        <h2>Содержимое сумки</h2>
        <p class="description">Выберите предмет слева, чтобы увидеть его изображение, редкость, описание и характеристики.</p>
        <div class="stats">
          <div class="stat"><span>Количество</span><strong>—</strong></div>
          <div class="stat"><span>Стоимость</span><strong>—</strong></div>
        </div>
      </aside>
    </div>
    <div class="notice" id="notice">Откройте инвентарь из Telegram Mini App, чтобы загрузить предметы.</div>
  </main>

  <script>
    const state = { items: [], filter: "all", selected: null, query: "", sort: "name" };
    const rarityNames = { common: "Обычный", rare: "Редкий", epic: "Эпический", legendary: "Легендарный" };
    const rarityOrder = { legendary: 4, epic: 3, rare: 2, common: 1 };
    const locationMeta = {
      field: { label: "Поле", symbol: "✧", order: 1 },
      forest: { label: "Лес", symbol: "♧", order: 2 },
      ruins: { label: "Руины", symbol: "⚑", order: 3 },
      darkforest: { label: "Тёмный лес", symbol: "☾", order: 4 }
    };
    const $ = id => document.getElementById(id);

    function locationLabel(location) {
      const meta = locationMeta[location];
      if (meta) return meta.label;
      return String(location).replace(/[_-]+/g, " ").replace(/^./, char => char.toLocaleUpperCase("ru"));
    }

    function renderLocationFilters() {
      const tabs = $("tabs");
      const locations = [...new Set(
        state.items.map(item => String(item.location || "").trim()).filter(Boolean)
      )].sort((a, b) => {
        const orderA = locationMeta[a]?.order ?? 100;
        const orderB = locationMeta[b]?.order ?? 100;
        return orderA - orderB || locationLabel(a).localeCompare(locationLabel(b), "ru");
      });

      if (state.filter !== "all" && !locations.includes(state.filter)) {
        state.filter = "all";
      }

      const fragment = document.createDocumentFragment();
      const allButton = document.createElement("button");
      allButton.className = "tab" + (state.filter === "all" ? " active" : "");
      allButton.dataset.filter = "all";
      allButton.dataset.symbol = "✧";
      allButton.textContent = "Все";
      fragment.append(allButton);

      locations.forEach(location => {
        const meta = locationMeta[location] || {};
        const button = document.createElement("button");
        button.className = "tab" + (state.filter === location ? " active" : "");
        button.dataset.filter = location;
        button.dataset.symbol = meta.symbol || "◇";
        button.textContent = locationLabel(location);
        fragment.append(button);
      });

      tabs.replaceChildren(fragment);
    }

    function visibleItems() {
      return state.items.filter(item =>
        (state.filter === "all" || item.location === state.filter) &&
        String(item.name || "").toLocaleLowerCase("ru").includes(state.query)
      ).sort((a,b) => {
        if (state.sort === "count") return (b.count || 0) - (a.count || 0);
        if (state.sort === "rarity") return (rarityOrder[b.rarity] || 0) - (rarityOrder[a.rarity] || 0);
        return String(a.name || "").localeCompare(String(b.name || ""), "ru");
      });
    }

    function render() {
      const list = visibleItems();
      $("total").textContent = list.length + " предметов";
      $("items").replaceChildren();
      if (!list.length) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = state.items.length ? "Ничего не найдено." : "Инвентарь пока пуст.";
        $("items").append(empty);
        return;
      }
      const fragment = document.createDocumentFragment();
      list.forEach(item => {
        const button = document.createElement("button");
        button.className = "item " + (item.rarity || "common") + (state.selected === item.id ? " selected" : "");
        button.type = "button";
        button.setAttribute("aria-label", item.name + ", количество " + item.count);
        const icon = document.createElement("span");
        icon.className = "item-icon";
        if (item.image) {
          const image = document.createElement("img");
          image.src = item.image;
          image.alt = "";
          image.loading = "lazy";
          image.decoding = "async";
          image.onerror = () => { icon.textContent = item.icon || "✦"; };
          icon.append(image);
        } else {
          icon.textContent = item.icon || "✦";
        }
        const name = document.createElement("span");
        name.className = "item-name";
        name.textContent = item.name;
        const quantity = document.createElement("span");
        quantity.className = "quantity";
        quantity.textContent = "×" + item.count;
        button.append(icon,name,quantity);
        button.addEventListener("click", () => { state.selected = item.id; render(); renderDetail(item); });
        fragment.append(button);
      });
      $("items").append(fragment);
    }

    function renderDetail(item, open = true) {
      const panel = $("detail");
      panel.replaceChildren();
      const add = (tag, cls, value) => {
        const el = document.createElement(tag);
        if (cls) el.className = cls;
        el.textContent = value;
        panel.append(el);
        return el;
      };
      const head = add("div","detail-head","");
      const headText = document.createElement("span");
      headText.textContent = "Сведения о предмете";
      head.append(headText);
      const close = document.createElement("button");
      close.type = "button";
      close.className = "detail-close";
      close.setAttribute("aria-label","Закрыть сведения");
      close.textContent = "×";
      close.addEventListener("click", () => panel.classList.remove("open"));
      head.append(close);
      if (open) panel.classList.add("open");
      const art = add("div","art","");
      if (item.image) {
        const image = document.createElement("img");
        image.className = "detail-image";
        image.src = item.image;
        image.alt = item.name || "";
        image.decoding = "async";
        image.onerror = () => { art.textContent = item.icon || "✦"; };
        art.append(image);
      } else {
        art.textContent = item.icon || "✦";
      }
      add("div","rarity " + (item.rarity || "common"),rarityNames[item.rarity] || "Неизвестная редкость");
      add("h2","",item.name || "Без названия");
      add("p","description",item.description || "Об этом предмете пока ничего не известно.");
      const stats = document.createElement("div"); stats.className = "stats";
      [[ "Количество", item.count ],[ "Стоимость за штуку", (item.cost ?? "—") + (item.cost != null ? " золота" : "") ],[ "Общая стоимость", item.cost != null ? (item.cost * item.count) + " золота" : "—" ]].forEach(([label,value]) => {
        const row = document.createElement("div"); row.className = "stat";
        const left = document.createElement("span"); left.textContent = label;
        const right = document.createElement("strong"); right.textContent = value;
        row.append(left,right); stats.append(row);
      });
      panel.append(stats);
    }

    $("tabs").addEventListener("click", event => {
      const button = event.target.closest("button[data-filter]");
      if (!button) return;
      state.filter = button.dataset.filter;
      $("tabs").querySelectorAll(".tab").forEach(tab => tab.classList.toggle("active", tab === button));
      render();
    });
    $("search").addEventListener("input", event => { state.query = event.target.value.trim().toLocaleLowerCase("ru"); render(); });
    $("sort").addEventListener("change", event => { state.sort = event.target.value; render(); });

    async function loadInventory() {
      try {
        const initData = window.Telegram?.WebApp?.initData || "";
        if (!initData) {
          throw new Error("Откройте инвентарь из Telegram Mini App.");
        }
        const response = await fetch("/inventory/data", {
          method: "GET",
          headers: {
            "Accept": "application/json",
            "X-Telegram-Init-Data": initData
          }
        });
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.error || "Сервер вернул HTTP " + response.status);
        }
        const data = await response.json();
        state.items = Array.isArray(data) ? data : (data.items || []);
        renderLocationFilters();
        if (data.gold != null) $("gold").textContent = data.gold;
        $("notice").hidden = true;
        if (state.items.length) {
          state.selected = state.items[0].id;
        }
        render();
        const selectedItem = state.items.find(item => item.id === state.selected);
        if (selectedItem) renderDetail(selectedItem, false);
      } catch (error) {
        $("items").replaceChildren();
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = error.message;
        $("items").append(empty);
        $("notice").textContent = "Данные инвентаря доступны только внутри Telegram Mini App.";
        console.info("Mobifield inventory:", error.message);
      }
    }
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }
    loadInventory();
  </script>
</body>
</html>