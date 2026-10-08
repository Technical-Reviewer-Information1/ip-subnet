(function () {
  'use strict';
  const T = window.Tools, $ = id => document.getElementById(id);
  const WEIGHT = [128, 64, 32, 16, 8, 4, 2, 1];

  let bits = '10101100000100001110111001111010'.split('').map(Number);

  const toOctets = b => [0, 1, 2, 3].map(i => b.slice(i * 8, i * 8 + 8));
  const octVal = o => o.reduce((a, v, i) => a + v * WEIGHT[i], 0);
  const ipStr = b => toOctets(b).map(octVal).join('.');
  const binStr = b => toOctets(b).map(o => o.join('')).join('.');
  function parseIp(s) {
    const p = String(s).trim().split('.');
    if (p.length !== 4) return null;
    const out = [];
    for (const x of p) {
      const v = parseInt(x, 10);
      if (!Number.isInteger(v) || v < 0 || v > 255) return null;
      for (let i = 0; i < 8; i++) out.push((v >> (7 - i)) & 1);
    }
    return out;
  }
  const prefixBits = n => Array.from({ length: 32 }, (_, i) => i < n ? 1 : 0);
  function maskToPrefix(b) {
    let n = 0;
    for (let i = 0; i < 32; i++) { if (b[i] === 1) n++; else break; }
    for (let i = n; i < 32; i++) if (b[i] === 1) return -1;   // 連続していない
    return n;
  }

  /* ---------- STEP1 ---------- */
  function drawOcts() {
    const box = $('octs'); box.innerHTML = '';
    toOctets(bits).forEach((o, oi) => {
      const d = document.createElement('div');
      d.className = 'oct';
      const bb = document.createElement('div'); bb.className = 'bits';
      o.forEach((v, i) => {
        const b = document.createElement('button');
        b.className = 'b' + (v ? ' on' : '');
        b.textContent = v;
        b.addEventListener('click', () => { bits[oi * 8 + i] = 1 - bits[oi * 8 + i]; drawAll(); });
        bb.appendChild(b);
      });
      const w = document.createElement('div'); w.className = 'w';
      WEIGHT.forEach(x => { const s = document.createElement('span'); s.textContent = x; w.appendChild(s); });
      const dec = document.createElement('div'); dec.className = 'dec'; dec.textContent = octVal(o);
      const lbl = document.createElement('div'); lbl.className = 'lbl'; lbl.textContent = (oi + 1) + 'つ目';
      d.appendChild(bb); d.appendChild(w); d.appendChild(dec); d.appendChild(lbl);
      box.appendChild(d);
    });
    $('ipLine').innerHTML = binStr(bits) + '<br><span style="font-size:1.9rem">' + ipStr(bits) + '</span>';
  }

  /* ---------- STEP2 ---------- */
  function drawMask() {
    const p = +$('prefix').value;
    $('prefixV').textContent = p;
    const mb = prefixBits(p);
    $('maskText').textContent = ipStr(mb);
    const hostBits = 32 - p;
    const mbar = $('maskBar');
    if (!mbar.querySelector('.net')) mbar.innerHTML = '<span class="net"></span><span class="host"></span>';
    const nEl = mbar.querySelector('.net'), hEl = mbar.querySelector('.host');
    nEl.style.width = (p / 32 * 100) + '%'; nEl.textContent = 'ネットワーク部 ' + p + 'ビット';
    hEl.style.width = (hostBits / 32 * 100) + '%'; hEl.textContent = 'ホスト部 ' + hostBits + 'ビット';
    $('binIp').innerHTML = 'IP　　　 ' + colorBin(bits, p);
    $('binMask').innerHTML = 'マスク　 ' + colorBin(mb, p);
    const theory = Math.pow(2, hostBits);
    $('mNet').textContent = p;
    $('mHost').textContent = hostBits;
    $('mTheory').textContent = theory.toLocaleString('ja-JP');
    $('mUsable').textContent = Math.max(0, theory - 2).toLocaleString('ja-JP');
    const na = bits.map((v, i) => i < p ? v : 0);
    const ba = bits.map((v, i) => i < p ? v : 1);
    $('mNetAddr').textContent = ipStr(na);
    $('mBcast').textContent = ipStr(ba);
    const n = $('maskNote');
    n.className = 'note info';
    n.innerHTML = 'サブネットマスク <strong>' + ipStr(mb) + '</strong>（/' + p + '）のとき、ホスト部は <strong>' + hostBits +
      'ビット</strong>。理論上は 2<sup>' + hostBits + '</sup> ＝ <strong>' + theory.toLocaleString('ja-JP') +
      '</strong> 個のアドレスがありますが、ネットワークアドレスとブロードキャストアドレスを除くので、' +
      '実際に接続できるのは <strong>' + Math.max(0, theory - 2).toLocaleString('ja-JP') + ' 台</strong>です。' +
      (p === 24 ? '<br>本文の例（255.255.255.0）はこれ。ホスト部8ビット → 256個 → <strong>254台</strong>です。' : '');
  }
  function colorBin(b, p) {
    return toOctets(b).map((o, oi) => o.map((v, i) => {
      const idx = oi * 8 + i;
      return '<span class="' + (idx < p ? 'np' : 'hp') + '">' + v + '</span>';
    }).join('')).join('<span style="color:var(--ink-3)">.</span>');
  }

  /* ---------- STEP3 判定 ---------- */
  function judge() {
    const a = parseIp($('ipA').value), b = parseIp($('ipB').value), m = parseIp($('maskIn').value);
    const n = $('judgeNote');
    if (!a || !b || !m) {
      n.className = 'note ng';
      n.textContent = 'IPアドレスまたはサブネットマスクの形式が正しくありません（例：192.168.1.1）。';
      return;
    }
    const p = maskToPrefix(m);
    if (p < 0) {
      n.className = 'note ng';
      n.textContent = 'サブネットマスクは、1が左から連続している必要があります（例：255.255.252.0）。';
      return;
    }
    $('binA').innerHTML = colorBin(a, p);
    $('binB').innerHTML = colorBin(b, p);
    $('binM').innerHTML = colorBin(m, p);
    let same = true, firstDiff = -1;
    for (let i = 0; i < p; i++) if (a[i] !== b[i]) { same = false; if (firstDiff < 0) firstDiff = i; }
    const na = ipStr(a.map((v, i) => i < p ? v : 0));
    const nb = ipStr(b.map((v, i) => i < p ? v : 0));
    n.className = same ? 'note ok' : 'note ng';
    n.innerHTML = same
      ? '<strong>同じネットワークです。</strong>ネットワーク部（左から ' + p + 'ビット）がどちらも一致しています（' + na + '）。' +
        'この2台は<strong>直接通信できます</strong>。'
      : '<strong>ちがうネットワークです。</strong>ネットワークアドレスは A が ' + na + '、B が ' + nb + '。' +
        '左から ' + (firstDiff + 1) + ' ビット目でちがっています（オレンジの部分）。この2台が通信するには<strong>ルータが必要</strong>です。';
  }

  /* ---------- STEP4 クイズ ---------- */
  const QUIZ = [
    { t: 'IPv4は32ビットで表される。割り当てられるIPアドレスは何通りか。',
      choices: ['2の32乗', '32', '2の96乗', '4'], a: '2の32乗',
      why: '1ビットで2通りなので、32ビットでは 2の32乗（約43億）通りです。' },
    { t: 'インターネットに直接接続されている端末に割り当てられるのはどれか。',
      choices: ['グローバルIPアドレス', 'プライベートIPアドレス', 'ネットワークアドレス', 'ブロードキャストアドレス'],
      a: 'グローバルIPアドレス',
      why: '世界で重複しないアドレスです。組織内だけで使うのがプライベートIPアドレスです。' },
    { t: 'IPv6が使われるようになった理由として適当なものはどれか。',
      choices: ['インターネットに直接接続する機器の増加に対応するため', '大容量データの送受信に対応するため',
                '無線LANに対応するため', '漢字のドメイン名に対応するため'],
      a: 'インターネットに直接接続する機器の増加に対応するため',
      why: 'スマートフォンや家電などがインターネットにつながるようになり、IPv4のアドレスが足りなくなったためです。' },
    { t: 'IPv6はIPv4の何倍のアドレスを割り当てられるか。',
      choices: ['2の96乗倍', '4倍', '2の32乗倍', '96倍'], a: '2の96乗倍',
      why: '128ビット − 32ビット ＝ 96ビットの差なので、2の96乗倍です。' },
    { t: '2進法「10101100.00010000.11101110.01111010」を10進法で表すとどうなるか。',
      choices: ['172.16.238.122', '172.16.238.12', '172.16.239.122', '172.17.238.122'], a: '172.16.238.122',
      why: '10101100 ＝ 128+32+8+4 ＝ 172、00010000 ＝ 16、11101110 ＝ 128+64+32+8+4+2 ＝ 238、01111010 ＝ 64+32+16+8+2 ＝ 122。' },
    { t: 'サブネットマスクが255.255.255.0のとき、ホスト部は何ビットか。',
      choices: ['8', '4', '12', '24'], a: '8',
      why: '255.255.255.0 は1が24個並ぶので、残り 32 − 24 ＝ 8ビットがホスト部です。' },
    { t: 'ホスト部が8ビットのとき、理論上いくつのアドレスがあるか。',
      choices: ['256', '128', '64', '512'], a: '256',
      why: '2の8乗 ＝ 256 です。' },
    { t: 'ホスト部が8ビットのとき、実際に接続できる端末は何台か。',
      choices: ['254', '256', '255', '128'], a: '254',
      why: '256からネットワークアドレスとブロードキャストアドレスの2つを引いて254台です。' },
    { t: 'サブネットマスクが255.255.252.0のとき、192.168.57.123 と直接通信できないのはどれか。',
      choices: ['192.168.55.50', '192.168.56.123', '192.168.57.50', '192.168.57.254'], a: '192.168.55.50',
      why: '255.255.252.0 は3つ目の区切りの上位6ビットまでがネットワーク部。57 ＝ 00111001 なので、同じネットワークは 56〜59。' +
        '55 は 00110111 で範囲外なので、直接通信できません。' }
  ];
  let qList = [], qi = 0, qScore = 0;
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  function startQuiz() { qList = shuffle(QUIZ); qi = 0; qScore = 0; renderQ(); }
  function renderQ() {
    if (qi >= qList.length) {
      $('qText').textContent = qScore + ' / ' + qList.length + ' 問正解';
      $('qChoices').innerHTML = ''; $('qFb').hidden = true; $('qNext').disabled = true;
      $('qProgress').textContent = qList.length + ' / ' + qList.length; return;
    }
    const it = qList[qi];
    $('qProgress').textContent = (qi + 1) + ' / ' + qList.length;
    $('qScore').textContent = qScore;
    $('qText').textContent = it.t;
    const box = $('qChoices'); box.className = 'choice4'; box.innerHTML = '';
    shuffle(it.choices).forEach(c => {
      const b = document.createElement('button');
      b.className = 'btn'; b.textContent = c; b.dataset.c = c;
      b.addEventListener('click', () => answerQ(c));
      box.appendChild(b);
    });
    $('qFb').hidden = true; $('qNext').disabled = true;
    $('qNext').textContent = (qi === qList.length - 1) ? '結果を見る' : '次の問題';
  }
  function answerQ(c) {
    const it = qList[qi], ok = c === it.a, box = $('qChoices');
    box.classList.add('locked');
    [...box.children].forEach(b => {
      if (b.dataset.c === it.a) b.classList.add('correct');
      else if (b.dataset.c === c) b.classList.add('wrong');
    });
    if (ok) qScore++;
    const fb = $('qFb');
    fb.className = 'note ' + (ok ? 'ok' : 'ng');
    fb.innerHTML = (ok ? '正解。' : '正解は「<strong>' + it.a + '</strong>」。') + it.why;
    fb.hidden = false;
    $('qScore').textContent = qScore; $('qNext').disabled = false;
  }

  function drawAll() { drawOcts(); drawMask(); }

  /* 本文の問題 */
  function drawBook() {
    if (!document.getElementById('bookBox')) return;
    window.Quiz.choice('bookBox', 'bookNote', [{"k": "ア", "q": "IPv4は32ビットなので、何通りのIPアドレスを割り当てられるか。", "ch": ["4", "8", "32", "96", "2⁴", "2⁸", "2³²", "2⁹⁶"], "a": 6, "why": "1ビットで2通りなので、32ビットでは 2³² 通り（約43億通り）です。"}, {"k": "イ", "q": "インターネットに接続されている端末に割り当てられているIPアドレスは。", "ch": ["ネットワーク", "プライベート", "グローバル", "ブロードキャスト"], "a": 2, "why": "インターネット上で重複しないように割り当てられるのがグローバルIPアドレス。家庭やLANの中だけで使うのがプライベートIPアドレスです。"}, {"k": "ウ", "q": "IPv6が使われるようになった理由は。", "ch": ["有線LANだけでなく無線LANにも対応するため", "大容量データの送受信に対応するため", "インターネットに直接接続する機器の増加に対応するため", "漢字などのドメイン名に対応するため", "HTMLの仕様変更に対応するため"], "a": 2, "why": "スマートフォンやIoT機器が増え、2³²（約43億）では足りなくなったためです。"}, {"k": "エ", "q": "IPv6はIPv4の何倍のIPアドレスを割り当てられるか。", "ch": ["4", "8", "32", "96", "2⁴", "2⁸", "2³²", "2⁹⁶"], "a": 7, "why": "2¹²⁸ ÷ 2³² ＝ 2⁹⁶ 倍です。指数の引き算になります。"}, {"k": "カ", "q": "IPアドレス「192.168.2.0」／サブネットマスク「255.255.255.0」のとき、ホスト部は何ビットか。", "ch": ["4", "8", "12", "24"], "a": 1, "why": "サブネットマスクの1が24個、0が8個。0の側がホスト部なので8ビットです。"}, {"k": "キ", "q": "理論的には何台の端末が接続可能か。", "ch": ["64", "128", "256", "512"], "a": 2, "why": "ホスト部8ビットなので 2⁸＝256通りです。"}, {"k": "ク", "q": "実際には何台の端末が接続可能か。", "ch": ["126", "127", "128", "254", "255", "256"], "a": 3, "why": "256からネットワークアドレスとブロードキャストアドレスの2つを引いて254台です。<strong>「−2」を忘れないこと。</strong>"}, {"k": "ケ", "q": "サブネットマスクが「255.255.252.0」のとき、「192.168.57.123」と直接通信できないのはどれか。", "ch": ["192.168.55.50", "192.168.56.123", "192.168.57.50", "192.168.57.254"], "a": 0, "why": "第3オクテットの上位6ビットまでがネットワーク部。57は 00111001、55は 00110111 で上位6ビットが異なります（56〜59が同じネットワーク）。"}], "本文の答えは【ア】⑥　【イ】②　【ウ】②　【エ】⑦　【カ】①　【キ】②　【ク】③　【ケ】⓪ です。");
  }

  function init() {
    document.querySelectorAll('[data-ip]').forEach(b => b.addEventListener('click', () => {
      bits = b.dataset.ip.replace(/\./g, '').split('').map(Number); drawAll();
    }));
    $('randIp').addEventListener('click', () => {
      bits = Array.from({ length: 32 }, () => Math.random() < .5 ? 1 : 0); drawAll();
    });
    $('prefix').addEventListener('input', drawMask);
    $('judge').addEventListener('click', judge);
    ['ipA', 'ipB', 'maskIn'].forEach(i => $(i).addEventListener('input', judge));
    document.querySelectorAll('[data-pair]').forEach(b => b.addEventListener('click', () => {
      const [x, y] = b.dataset.pair.split('|');
      $('ipA').value = x; $('ipB').value = y; judge();
    }));
    $('qNext').addEventListener('click', () => { qi++; renderQ(); });
    $('qReset').addEventListener('click', startQuiz);
    window.Terms.glossary($('glossBox'), ['IPアドレス', 'IPv4', 'IPv6', 'グローバルIPアドレス', 'プライベートIPアドレス',
      'ネットワーク部', 'ホスト部', 'サブネットマスク', 'ネットワークアドレス', 'ブロードキャストアドレス', 'ルータ']);
    drawAll(); judge(); startQuiz();
    drawBook();
    window.Terms.attach();
  }
  if (window.Predict) Predict.make('pdI', {
    q: 'サブネットマスクを <span class="mono">255.255.255.0</span>（254台）から <span class="mono">255.255.252.0</span> に変えると、つなげる端末の数はどうなるでしょう？',
    type: 'pick',
    ch: ['4分の1に減る', 'ほとんど変わらない', '約4倍に増える', '2倍に増える'],
    answer: function () { return 2; },
    show: function () {
      return '<span class="mono">252 ＝ 11111100<sub>(2)</sub></span> なので「1」は22ビット分。ホスト部は<strong>10ビット</strong>になります。' +
             '<span class="mono">2<sup>10</sup> − 2 ＝ 1022台</span>で、254台の<strong>約4倍</strong>です。';
    },
    why: '「252は255より小さいから減りそう」と思いがちですが、逆です。' +
         'マスクの「1」が<strong>減る</strong>ほどネットワーク部がせまくなり、残りの<strong>ホスト部が広がる</strong>ので、つなげる台数は増えます。' +
         'マスクは「どこまでが同じネットワークか」の境目を決めているだけです。'
  });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
