// UI Controller & Screen Management for MOMO MAZE
// 19 screens, mobile-first, all wired and functional
import { CAMPAIGN_LEVELS } from './game_data.js';
import { SKINS } from './character.js';
import { GHOST_TYPES } from './ghosts.js';
import { audio } from './audio.js';

// ─── Save-state (simple localStorage) ────────────────────────
const SAVE_KEY = 'momomaze_save_v3';
function loadSave() {
  try { return JSON.parse(localStorage.getItem(SAVE_KEY)) || { lastLevel: 1, stars: {} }; }
  catch { return { lastLevel: 1, stars: {} }; }
}
function writeSave(data) {
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(data)); } catch {}
}
export const saveData = loadSave();

// ─── Loading tips ─────────────────────────────────────────────
const TIPS = [
  '🌸 Tip: Collect all momos before going for the Golden Momo!',
  '👻 Tip: Spirits multiply over time — work fast!',
  '🗺️ Tip: Press M to open your Garden Blueprint map.',
  '🌿 Tip: Golumolu can slide along hedge walls — use it!',
  '⭐ Tip: Finish faster and with more hearts for 3 stars.',
  '🥟 Tip: The Golden Momo is in the central sanctuary.',
  '🔑 Tip: Eating the Golden Momo opens the Leaf Gate exit!',
];

// ─── Sticker definitions ──────────────────────────────────────
const STICKERS = [
  { id: 'cherry_blossom', name: 'Sakura', icon: '🌸', unlock: 'Complete Chapter 1' },
  { id: 'mushroom',       name: 'Shroom',  icon: '🍄', unlock: 'Complete Level 5 fast' },
  { id: 'star_gold',      name: 'Gold Star',icon: '⭐', unlock: 'Get 3 stars on any level' },
  { id: 'heart',          name: 'Big Heart',icon: '❤️', unlock: 'Finish with 3 hearts' },
  { id: 'momo',           name: 'Steamy',  icon: '🥟', unlock: 'Collect 50 momos total' },
  { id: 'rainbow',        name: 'Rainbow', icon: '🌈', unlock: 'Complete Chapter 2' },
  { id: 'moon',           name: 'Moon',    icon: '🌙', unlock: 'Play after sunset' },
  { id: 'garden',         name: 'Garden',  icon: '🌿', unlock: 'Complete Chapter 3' },
  { id: 'butterfly',      name: 'Flutter', icon: '🦋', unlock: 'Never get tagged in a level' },
  { id: 'fox',            name: 'Fox',     icon: '🦊', unlock: 'Complete Chapter 4' },
  { id: 'cloud',          name: 'Cloudy',  icon: '☁️',  unlock: 'Complete Chapter 5' },
  { id: 'trophy',         name: 'Trophy',  icon: '🏆', unlock: 'Complete all 25 levels' },
];

// ─── Closet data ──────────────────────────────────────────────
const CLOSET_DATA = {
  outfits: [
    { id: 'cream',        name: 'Classic Honey', icon: '🟡', unlocked: true },
    { id: 'golden_momo',  name: 'Golden Momo',   icon: '✨', unlocked: true },
    { id: 'berry_blossom',name: 'Berry Blossom', icon: '🌸', unlocked: false },
    { id: 'matcha',       name: 'Matcha Meadow', icon: '🍵', unlocked: false },
    { id: 'sakura',       name: 'Sakura Dream',  icon: '🌸', unlocked: false },
    { id: 'ocean',        name: 'Ocean Breeze',  icon: '🌊', unlocked: false },
  ],
  hats: [
    { id: 'none',       name: 'No Hat',       icon: '—',   unlocked: true },
    { id: 'flower',     name: 'Daisy Crown',  icon: '🌼',  unlocked: true },
    { id: 'chef',       name: "Chef's Hat",   icon: '👨‍🍳', unlocked: false },
    { id: 'wizard',     name: 'Garden Wizard',icon: '🧙',  unlocked: false },
  ],
  accessories: [
    { id: 'none',   name: 'None',    icon: '—',  unlocked: true },
    { id: 'scarf',  name: 'Scarf',   icon: '🧣', unlocked: true },
    { id: 'bow',    name: 'Big Bow', icon: '🎀', unlocked: false },
  ],
  trails: [
    { id: 'sparkle', name: 'Sparkle', icon: '✨', unlocked: true },
    { id: 'petals',  name: 'Petals',  icon: '🌸', unlocked: false },
    { id: 'hearts',  name: 'Hearts',  icon: '💕', unlocked: false },
  ],
};

// ─── Chapter definitions ──────────────────────────────────────
const CHAPTERS = [
  { id: 1, name: 'The Little Meadow',   levels: [1,2,3,4,5],    reward: '🌸 Sakura Golumolu sticker' },
  { id: 2, name: 'The Blooming Garden', levels: [6,7,8,9,10],   reward: '🌈 Rainbow sticker' },
  { id: 3, name: 'The Misty Forest',    levels: [11,12,13,14,15],reward: '🌿 Garden Spirit sticker' },
  { id: 4, name: 'The Golden Valley',   levels: [16,17,18,19,20],reward: '🦊 Fox sticker' },
  { id: 5, name: 'The Grand Finale',    levels: [21,22,23,24,25],reward: '🏆 Champion Trophy sticker' },
];

// ─────────────────────────────────────────────────────────────
export class UIManager {
  constructor(game) {
    this.game = game;
    this.currentScreen = 'splash';
    this.isPaused = false;
    this.isMapOpen = false;
    this.activeTab = { closet: 'outfits', spirit: 'follower', chapter: 1 };
    this.customConfig = { ghosts: 1, size: 12, speed: 1.0, gates: false, timeLimit: false };
    this.pendingLevelId = 1;
    this.tutStep = 0;

    this._cacheDOM();
    this._bindGlobal();
    this._bindScreenButtons();
    this._buildLevelMap();
    this._buildCloset('outfits');
    this._buildSpiritBook('follower');
    this._buildStickers();

    // Show splash on start
    this.showScreen('splash');
  }

  // ── DOM cache ───────────────────────────────────────────────
  _cacheDOM() {
    this.minimapCanvas  = document.getElementById('minimap-canvas');
    this.minimapCtx     = this.minimapCanvas?.getContext('2d');
    this.fullmapCanvas  = document.getElementById('fullmap-canvas');
    this.fullmapCtx     = this.fullmapCanvas?.getContext('2d');

    this.hudLives       = document.getElementById('hud-lives');
    this.hudMomos       = document.getElementById('hud-momos');
    this.hudTimer       = document.getElementById('hud-timer');
    this.hudGateLabel   = document.getElementById('hud-gate-label');
    this.hudGhostCount  = document.getElementById('hud-ghost-count');

    this.vicTitle       = document.getElementById('vic-title');
    this.vicTime        = document.getElementById('vic-time');
    this.vicMomos       = document.getElementById('vic-momos');
    this.vicHearts      = document.getElementById('vic-hearts');
    this.vicStars       = document.getElementById('vic-stars');

    this.pauseInfo      = document.getElementById('pause-info');
    this.pauseLives     = document.getElementById('pause-lives');
    this.pauseMomos     = document.getElementById('pause-momos');
    this.pauseTime      = document.getElementById('pause-time');

    this.loadingBar     = document.getElementById('loading-bar');
    this.loadingTip     = document.getElementById('loading-tip');
    this.playSaveInfo   = document.getElementById('play-save-info');
    this.playMenuLevelLabel = document.getElementById('play-menu-level-label');
    this.invulnFlash    = document.getElementById('invuln-flash');

    this.joystickBase   = document.getElementById('virtual-joystick');
    this.joystickStick  = document.getElementById('joystick-stick');
  }

  // ── All screens list ────────────────────────────────────────
  _allScreenIds() {
    return [
      'splash','menu','play-menu','levels','level-preview',
      'loading','tutorial','hud','pause','victory','defeat',
      'chapter','closet','spirits','stickers','custom',
      'settings','credits'
    ];
  }

  showScreen(name) {
    const domId = (name === 'game' || name === 'hud') ? 'hud' : name;
    this.currentScreen = (name === 'hud') ? 'game' : name;
    this._allScreenIds().forEach(id => {
      const el = document.getElementById(`screen-${id}`);
      if (el) el.classList.remove('active');
    });
    const target = document.getElementById(`screen-${domId}`);
    if (target) target.classList.add('active');

    // Update dynamic level label on Play Menu when opened
    if (name === 'play-menu') {
      const lvlLabel = document.getElementById('play-menu-level-label');
      if (lvlLabel) {
        lvlLabel.textContent = `Level ${saveData.lastLevel || 1}`;
      }
    }

    // Map overlay is separate (doesn't replace HUD)
    if (domId !== 'hud') {
      const mo = document.getElementById('map-overlay');
      if (mo) mo.classList.remove('active');
    }
  }

  // ── Splash → Menu ───────────────────────────────────────────
  _bindGlobal() {
    const splashEl = document.getElementById('screen-splash');

    const dismissSplash = () => {
      if (this.currentScreen !== 'splash') return;
      try {
        audio.init();
        audio.playClick();
        audio.startBGM();
      } catch (err) {
        console.warn('Audio start on splash:', err);
      }
      if (splashEl) splashEl.classList.add('leaving');
      setTimeout(() => {
        this.showScreen('menu');
        if (splashEl) splashEl.classList.remove('leaving');
      }, 180);
    };

    // Splash: click or tap anywhere
    splashEl?.addEventListener('click', () => dismissSplash());
    splashEl?.addEventListener('pointerdown', () => dismissSplash());

    // Splash: Press Any Key to Continue
    window.addEventListener('keydown', (e) => {
      if (this.currentScreen === 'splash') {
        dismissSplash();
        return;
      }
      const isPlay = (this.currentScreen === 'game' || this.currentScreen === 'hud');
      if (e.key === 'Escape' || e.key === 'p' || e.key === 'P') {
        if (isPlay) this.togglePause();
        else if (this.currentScreen === 'pause') this.togglePause(false);
      }
      if ((e.key === 'm' || e.key === 'M') && isPlay) {
        this.toggleMapOverlay();
      }
      if ((e.key === 'c' || e.key === 'C') && isPlay) {
        this.game.toggleCameraMode();
      }
    });

    // Data-back buttons (close / back buttons carry data-back attr)
    document.addEventListener('click', e => {
      const btn = e.target.closest('[data-back]');
      if (btn) {
        audio.playClick();
        this.showScreen(btn.dataset.back);
      }
    });

    this._setupVirtualJoystick();
  }

  // ── All button wiring ────────────────────────────────────────
  _bindScreenButtons() {
    const on = (id, fn) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('click', () => { audio.playClick(); fn(); });
    };

    // ── MENU ──
    // Clicking Play on main menu navigates to Screen 03 (Play Menu)!
    on('btn-play',         () => this.showScreen('play-menu'));
    on('btn-menu-levels',  () => this.showScreen('levels'));
    on('btn-menu-golumolu',() => this.showScreen('closet'));
    on('btn-menu-spirits', () => this.showScreen('spirits'));
    on('btn-menu-settings',() => this.showScreen('settings'));

    // Nav bar
    on('nav-levels',   () => this.showScreen('levels'));
    on('nav-golumolu', () => this.showScreen('closet'));
    on('nav-spirits',  () => this.showScreen('spirits'));
    on('nav-settings', () => this.showScreen('settings'));
    on('nav-credits',  () => this.showScreen('credits'));

    // ── PLAY MENU (Screen 03-B) ──
    on('btn-play-back',    () => this.showScreen('menu'));
    on('btn-continue',     () => this._launchLevel(saveData.lastLevel || 1));
    on('btn-new-game',     () => {
      saveData.lastLevel = 1;
      writeSave(saveData);
      this._launchLevel(1);
    });
    on('btn-custom-play',  () => this.showScreen('custom'));

    // Update save info when play-menu opens
    document.getElementById('btn-play')?.addEventListener('click', () => {
      if (this.playSaveInfo) {
        this.playSaveInfo.textContent = `Level ${saveData.lastLevel} · ${Object.values(saveData.stars || {}).reduce((a, b) => a + b, 0)} ⭐ total`;
      }
    });

    // ── LEVEL PREVIEW ──
    on('btn-preview-back',  () => this.showScreen('levels'));
    on('btn-preview-start', () => this._launchLevel(this.pendingLevelId));

    // ── HUD ──
    on('btn-hud-pause',  () => this.togglePause());
    on('btn-hud-map',    () => this.toggleMapOverlay());
    on('btn-hud-dash',   () => this.game.triggerDash());
    on('btn-hud-camera', () => this.game.toggleCameraMode());
    on('btn-close-map',  () => this.toggleMapOverlay(false));
    on('btn-close-map2', () => this.toggleMapOverlay(false));

    // ── PAUSE ──
    on('btn-resume',         () => this.togglePause(false));
    on('btn-restart',        () => { this.togglePause(false); this.game.restartLevel(); });
    on('btn-pause-settings', () => this.showScreen('settings'));
    on('btn-quit-menu',      () => { this.togglePause(false); this.game.quitToMenu(); });

    // ── VICTORY ──
    on('btn-vic-replay', () => { this.showScreen('hud'); this.game.restartLevel(); });
    on('btn-vic-next',   () => this._advanceLevel());
    on('btn-vic-menu',   () => this.game.quitToMenu());

    // ── DEFEAT ──
    on('btn-def-retry', () => { this.showScreen('hud'); this.game.restartLevel(); });
    on('btn-def-menu',  () => this.game.quitToMenu());

    // ── CHAPTER COMPLETE ──
    on('btn-chap-menu',     () => this.game.quitToMenu());
    on('btn-chap-continue', () => this._advanceLevel());

    // ── CUSTOM PLAY ──
    this._bindCustomPlay();
    on('btn-custom-start', () => this._launchCustom());

    // ── SETTINGS ──
    this._bindSettings();

    // ── TUTORIAL ──
    on('btn-tut-next', () => this._tutorialNext());

    // ── CLOSET tabs ──
    document.getElementById('closet-tabs')?.addEventListener('click', e => {
      const tab = e.target.closest('.closet-tab');
      if (!tab) return;
      document.querySelectorAll('.closet-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      this._buildCloset(tab.dataset.tab);
    });

    // ── SPIRIT tabs ──
    document.getElementById('spirit-tabs')?.addEventListener('click', e => {
      const tab = e.target.closest('.spirit-tab');
      if (!tab) return;
      document.querySelectorAll('.spirit-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      this._buildSpiritDetail(tab.dataset.spirit);
    });
  }

  // ── Level map builder ────────────────────────────────────────
  _buildLevelMap() {
    // Chapter tabs
    const tabRow = document.getElementById('chapter-tabs');
    if (tabRow) {
      tabRow.innerHTML = '';
      CHAPTERS.forEach(ch => {
        const tab = document.createElement('div');
        tab.className = `chap-tab ${ch.id === 1 ? 'active' : ''}`;
        tab.dataset.chap = ch.id;
        tab.textContent = `Ch.${ch.id}: ${ch.name}`;
        tab.addEventListener('click', () => {
          document.querySelectorAll('.chap-tab').forEach(t => t.classList.remove('active'));
          tab.classList.add('active');
          this._renderChapterLevels(ch.id);
        });
        tabRow.appendChild(tab);
      });
    }
    this._renderChapterLevels(1);
  }

  _renderChapterLevels(chapId) {
    const grid = document.getElementById('levels-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const chap = CHAPTERS.find(c => c.id === chapId);
    if (!chap) return;

    chap.levels.forEach(lvlId => {
      const cfg = CAMPAIGN_LEVELS.find(l => l.level_id === lvlId);
      if (!cfg) return;
      const stars = saveData.stars?.[lvlId] || 0;
      const isActive = lvlId === saveData.lastLevel;

      const node = document.createElement('div');
      node.className = `level-node ${isActive ? 'active-level' : ''}`;
      node.innerHTML = `
        <div class="level-node-num">${lvlId}</div>
        <div class="level-node-name">${cfg.name || `Level ${lvlId}`}</div>
        <div class="level-node-stars">${'⭐'.repeat(stars)}${'☆'.repeat(3 - stars)}</div>
      `;
      node.addEventListener('click', () => {
        audio.playClick();
        this._startLevelPreview(lvlId);
      });
      grid.appendChild(node);
    });
  }

  _startLevelPreview(lvlId) {
    this.pendingLevelId = lvlId;
    const cfg = CAMPAIGN_LEVELS.find(l => l.level_id === lvlId);
    if (cfg) {
      document.getElementById('preview-title').textContent = `Level ${lvlId}: ${cfg.name || ''}`;
      document.getElementById('preview-momos').textContent = cfg.target_momos || 8;
      document.getElementById('preview-size').textContent = `${cfg.grid_size}×${cfg.grid_size}`;
      document.getElementById('preview-ghosts').textContent = cfg.starting_spirits || 1;
      this._drawPreviewMaze(cfg);
    }
    this.showScreen('level-preview');
  }

  _drawPreviewMaze(cfg) {
    const canvas = document.getElementById('preview-maze-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width; const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    // Simple green/cream grid preview
    ctx.fillStyle = '#A9CA49'; ctx.fillRect(0, 0, w, h);
    const gridData = cfg.grid || [];
    if (gridData.length) {
      const size = gridData.length;
      const cell = w / size;
      gridData.forEach((row, y) => row.forEach((v, x) => {
        if (v === 1) {
          ctx.fillStyle = '#4E8C2A';
          ctx.fillRect(x * cell, y * cell, cell, cell);
        }
      }));
    }
  }

  _startSavedLevel() {
    this._startLevelPreview(saveData.lastLevel || 1);
  }

  // ── Loading screen then launch ───────────────────────────────
  _launchLevel(lvlId) {
    this.showScreen('loading');
    const tips = TIPS;
    if (this.loadingTip) this.loadingTip.textContent = tips[Math.floor(Math.random() * tips.length)];

    let progress = 0;
    const bar = this.loadingBar;
    const tick = setInterval(() => {
      progress += 12 + Math.random() * 20;
      if (bar) bar.style.width = Math.min(progress, 95) + '%';
      if (progress >= 95) {
        clearInterval(tick);
        setTimeout(() => {
          if (bar) bar.style.width = '100%';
          setTimeout(() => {
            this.game.startLevel(lvlId);
          }, 300);
        }, 200);
      }
    }, 120);
  }

  _advanceLevel() {
    const next = this.game.currentLevelId + 1;
    if (next > 25) {
      this.game.quitToMenu();
      return;
    }
    // Check if chapter boundary
    const chapBoundary = CHAPTERS.find(c => c.levels[c.levels.length - 1] === this.game.currentLevelId);
    if (chapBoundary && next <= 25) {
      this._showChapterComplete(chapBoundary, next);
    } else {
      this._launchLevel(next);
    }
  }

  _showChapterComplete(chap, nextLevel) {
    document.getElementById('chapter-name').textContent = `Chapter ${chap.id}: ${chap.name}`;
    document.getElementById('chapter-sub').textContent = `You cleared Levels ${chap.levels[0]}–${chap.levels[chap.levels.length - 1]}!`;
    document.getElementById('chapter-reward-name').textContent = chap.reward;
    this.showScreen('chapter');
    // Store next level for continue button
    this._chapterNextLevel = nextLevel;
    document.getElementById('btn-chap-continue').onclick = () => {
      audio.playClick();
      this._launchLevel(nextLevel);
    };
  }

  // ── Custom play ──────────────────────────────────────────────
  _bindCustomPlay() {
    // Chip groups
    ['ghosts', 'size', 'speed'].forEach(key => {
      const group = document.getElementById(`chip-${key}`);
      if (!group) return;
      group.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
          group.querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
          chip.classList.add('selected');
          this.customConfig[key] = key === 'ghosts' ? parseInt(chip.dataset.val)
            : key === 'size' ? parseInt(chip.dataset.val)
            : parseFloat(chip.dataset.val);
        });
      });
    });

    // Toggles
    ['gates', 'time'].forEach(key => {
      const id = key === 'gates' ? 'toggle-gates' : 'toggle-time';
      const toggle = document.getElementById(id);
      if (!toggle) return;
      toggle.addEventListener('click', () => {
        const isOn = toggle.classList.toggle('on');
        this.customConfig[key === 'gates' ? 'gates' : 'timeLimit'] = isOn;
      });
    });
  }

  _launchCustom() {
    this.game.startCustom(this.customConfig);
  }

  // ── Settings ─────────────────────────────────────────────────
  _bindSettings() {
    const muteToggle = document.getElementById('toggle-mute');
    if (muteToggle) {
      muteToggle.addEventListener('click', () => {
        const on = muteToggle.classList.toggle('on');
        audio.setMuted(on);
      });
    }
    const selCam = document.getElementById('sel-camera');
    if (selCam) selCam.onchange = e => this.game.setCameraMode(e.target.value);

    const sliderMaster = document.getElementById('slider-master');
    if (sliderMaster) sliderMaster.oninput = e => audio.setMasterVolume(e.target.value / 100);
  }

  // ── Closet builder ───────────────────────────────────────────
  _buildCloset(tab) {
    const container = document.getElementById('closet-items');
    if (!container) return;
    container.innerHTML = '';
    const items = CLOSET_DATA[tab] || CLOSET_DATA.outfits;
    items.forEach(item => {
      const div = document.createElement('div');
      const isSelected = tab === 'outfits' && item.id === this.game.currentSkin;
      div.className = `closet-item ${isSelected ? 'selected' : ''} ${item.unlocked ? '' : 'locked'}`;
      div.innerHTML = `
        <span class="item-icon">${item.icon}</span>
        <div class="item-name">${item.name}</div>
        ${!item.unlocked ? '<div class="item-lock">🔒</div>' : ''}
      `;
      if (item.unlocked) {
        div.addEventListener('click', () => {
          audio.playClick();
          if (tab === 'outfits') {
            this.game.setSkin(item.id);
            container.querySelectorAll('.closet-item').forEach(c => c.classList.remove('selected'));
            div.classList.add('selected');
          }
        });
      }
      container.appendChild(div);
    });
  }

  // ── Spirit book ──────────────────────────────────────────────
  _buildSpiritBook(firstKey) {
    const tabs = document.getElementById('spirit-tabs');
    if (!tabs) return;
    tabs.innerHTML = '';
    Object.entries(GHOST_TYPES).forEach(([key, g]) => {
      const tab = document.createElement('div');
      tab.className = `spirit-tab ${key === firstKey ? 'active' : ''}`;
      tab.dataset.spirit = key;
      tab.innerHTML = `<span class="tab-ghost">👻</span>${g.name}`;
      tab.addEventListener('click', () => {
        document.querySelectorAll('.spirit-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this._buildSpiritDetail(key);
      });
      tabs.appendChild(tab);
    });
    this._buildSpiritDetail(firstKey);
  }

  _buildSpiritDetail(key) {
    const g = GHOST_TYPES[key];
    if (!g) return;
    const detail = document.getElementById('spirit-detail');
    if (!detail) return;
    detail.innerHTML = `
      <div class="spirit-top">
        <div class="spirit-avatar">👻</div>
        <div>
          <div class="spirit-name">${g.name} Spirit</div>
          <div class="spirit-bio">${g.desc}</div>
        </div>
      </div>
      <div class="spirit-stats-grid">
        <div class="spirit-stat-item">
          <div class="spirit-stat-label">⚡ Speed</div>
          <div class="spirit-stat-val">${g.speed}×</div>
        </div>
        <div class="spirit-stat-item">
          <div class="spirit-stat-label">👁 Eye Style</div>
          <div class="spirit-stat-val">${g.eyeType}</div>
        </div>
        <div class="spirit-stat-item">
          <div class="spirit-stat-label">✨ Glow</div>
          <div class="spirit-stat-val" style="color:#${g.glow.toString(16)}">■ glow</div>
        </div>
        <div class="spirit-stat-item">
          <div class="spirit-stat-label">🕐 Appears</div>
          <div class="spirit-stat-val">${key === 'follower' ? 'Start' : key === 'cutter' ? '60s' : '180s'}</div>
        </div>
      </div>
      <div class="spirit-tip">
        💡 ${key === 'follower' ? 'Heads straight for Golumolu — stay moving to avoid it!'
            : key === 'cutter' ? 'Tries to predict your path and cut you off. Change direction often!'
            : 'Drifts through the maze randomly but fast. Keep your eyes everywhere!'}
      </div>
    `;
  }

  // ── Sticker book ─────────────────────────────────────────────
  _buildStickers() {
    const grid = document.getElementById('stickers-grid');
    if (!grid) return;
    grid.innerHTML = '';
    const count = document.getElementById('stickers-count');
    let unlocked = 0;
    STICKERS.forEach(s => {
      const have = saveData.stickers?.[s.id] || false;
      if (have) unlocked++;
      const card = document.createElement('div');
      card.className = `sticker-card ${have ? 'unlocked' : 'locked'}`;
      card.innerHTML = `<span class="sticker-icon">${have ? s.icon : '❓'}</span><div class="sticker-name">${s.name}</div>`;
      grid.appendChild(card);
    });
    if (count) count.textContent = `${unlocked} / ${STICKERS.length} Stickers`;
  }

  // ── Tutorial ─────────────────────────────────────────────────
  _tutorialNext() {
    this.tutStep++;
    if (this.tutStep >= 1) {
      // Only 1 page for now — go straight to play
      this.game.startLevel(1);
      this.tutStep = 0;
    }
  }

  // ── Pause / Map overlay ──────────────────────────────────────
  togglePause(forceState = null) {
    this.isPaused = forceState !== null ? forceState : !this.isPaused;
    const pauseScreen = document.getElementById('screen-pause');
    if (this.isPaused) {
      pauseScreen?.classList.add('active');
      const st = this.game.getState();
      if (this.pauseLives) this.pauseLives.textContent = st.lives;
      if (this.pauseMomos) this.pauseMomos.textContent = `${st.collectedMomos}/${st.targetMomos}`;
      if (this.pauseTime) {
        const m = Math.floor(st.elapsedTime / 60), s = Math.floor(st.elapsedTime % 60);
        this.pauseTime.textContent = `${m}:${s < 10 ? '0' : ''}${s}`;
      }
    } else {
      pauseScreen?.classList.remove('active');
    }
  }

  toggleMapOverlay(forceState = null) {
    this.isMapOpen = forceState !== null ? forceState : !this.isMapOpen;
    const overlay = document.getElementById('map-overlay');
    if (this.isMapOpen) {
      overlay?.classList.add('active');
      this.drawFullMap();
    } else {
      overlay?.classList.remove('active');
    }
  }

  // ── HUD Update ───────────────────────────────────────────────
  updateHUD(state) {
    // Lives (individual hearts)
    for (let i = 1; i <= 3; i++) {
      const h = document.getElementById(`h${i}`);
      if (h) h.classList.toggle('lost', i > state.lives);
    }

    if (this.hudMomos) this.hudMomos.textContent = `${state.collectedMomos} / ${state.targetMomos}`;

    // Timer
    if (this.hudTimer) {
      const m = Math.floor(state.elapsedTime / 60);
      const s = Math.floor(state.elapsedTime % 60);
      this.hudTimer.textContent = `${m}:${s < 10 ? '0' : ''}${s}`;
    }

    // Gate status
    if (this.hudGateLabel) {
      if (state.exitGateOpen) {
        this.hudGateLabel.textContent = '🟢 Gate Open!';
      } else if (state.hasMovingGates) {
        this.hudGateLabel.textContent = `Phase ${state.activePhase} · ${Math.ceil(state.phaseTimer)}s`;
      } else {
        this.hudGateLabel.textContent = 'Collect Momos';
      }
    }

    // Ghost count
    if (this.hudGhostCount) {
      this.hudGhostCount.textContent = `${state.ghosts.length}/3`;
    }

    // Minimap
    this.drawMinimap(state);
    if (this.isMapOpen) this.drawFullMap(state);
  }

  // ── Minimap render ───────────────────────────────────────────
  drawMinimap(state) {
    const ctx = this.minimapCtx;
    if (!ctx || !state?.mazeData) return;
    const canvas = this.minimapCanvas;
    const w = canvas.width; const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const grid = state.mazeData.grid;
    if (!grid) return;
    const size = state.mazeData.size;
    const cell = w / size;

    // Background
    ctx.fillStyle = '#B5D96A'; ctx.fillRect(0, 0, w, h);

    // Walls
    ctx.fillStyle = '#4E8C2A';
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        if (grid[y][x] === 1) ctx.fillRect(x * cell, y * cell, cell, cell);
      }
    }

    // Collectibles
    ctx.fillStyle = '#FFD54F';
    (state.mazeData.collectibles || []).forEach(c => {
      if (!c.collected) {
        ctx.beginPath();
        ctx.arc((c.x + 0.5) * cell, (c.y + 0.5) * cell, cell * 0.4, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    // Exit
    if (state.mazeData.exitGate) {
      ctx.fillStyle = '#FFA000';
      ctx.fillRect(state.mazeData.exitGate.x * cell, state.mazeData.exitGate.y * cell, cell, cell);
    }

    // Ghosts
    state.ghosts.forEach(g => {
      ctx.fillStyle = g.typeKey === 'cutter' ? '#FF7043' : (g.typeKey === 'wanderer' ? '#CE93D8' : '#FFF9C4');
      ctx.beginPath();
      ctx.arc((g.gridX + 0.5) * cell, (g.gridY + 0.5) * cell, cell * 0.6, 0, Math.PI * 2);
      ctx.fill();
    });

    // Player
    ctx.fillStyle = '#FF5722'; ctx.strokeStyle = '#FFF'; ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc((state.player.gridX + 0.5) * cell, (state.player.gridY + 0.5) * cell, cell * 0.75, 0, Math.PI * 2);
    ctx.fill(); ctx.stroke();
  }

  drawFullMap(state = this.game.getState()) {
    const ctx = this.fullmapCtx;
    if (!ctx || !state?.mazeData) return;
    const canvas = this.fullmapCanvas;
    const w = canvas.width; const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const grid = state.mazeData.grid;
    if (!grid) return;
    const size = state.mazeData.size;
    const cell = w / size;

    ctx.fillStyle = '#B5D96A'; ctx.fillRect(0, 0, w, h);

    ctx.fillStyle = '#3E7824';
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        if (grid[y][x] === 1) ctx.fillRect(x * cell, y * cell, cell, cell);
      }
    }

    (state.mazeData.collectibles || []).forEach(c => {
      if (!c.collected) {
        ctx.fillStyle = '#FFD54F';
        ctx.beginPath();
        ctx.arc((c.x + 0.5) * cell, (c.y + 0.5) * cell, cell * 0.5, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    if (state.mazeData.exitGate) {
      ctx.fillStyle = '#FFA000';
      ctx.fillRect(state.mazeData.exitGate.x * cell, state.mazeData.exitGate.y * cell, cell * 1.2, cell);
    }

    // Ghost path visited dots
    state.ghosts.forEach(g => {
      ctx.fillStyle = '#FFF9C4'; ctx.globalAlpha = 0.5;
      ctx.beginPath();
      ctx.arc((g.gridX + 0.5) * cell, (g.gridY + 0.5) * cell, cell * 0.6, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.globalAlpha = 1;

    // Player beacon
    ctx.fillStyle = '#E64A19';
    ctx.beginPath();
    ctx.arc((state.player.gridX + 0.5) * cell, (state.player.gridY + 0.5) * cell, cell * 0.85, 0, Math.PI * 2);
    ctx.fill();

    // Label
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.font = `bold ${Math.max(8, cell * 0.6)}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText('YOU', (state.player.gridX + 0.5) * cell, (state.player.gridY + 0.5) * cell + cell * 0.25);
  }

  // ── Victory / Defeat ─────────────────────────────────────────
  showVictory(stats) {
    audio.playWin();
    this.showScreen('victory');

    const m = Math.floor(stats.time / 60), s = Math.floor(stats.time % 60);
    if (this.vicTitle)  this.vicTitle.textContent  = `${stats.levelName} Clear!`;
    if (this.vicTime)   this.vicTime.textContent   = `${m}:${s < 10 ? '0' : ''}${s}`;
    if (this.vicMomos)  this.vicMomos.textContent  = `${stats.collected}/${stats.total}`;
    if (this.vicHearts) this.vicHearts.textContent = `${stats.lives}/3`;

    // Star rating
    let stars = 3;
    if (stats.time > 120) stars = 2;
    if (stats.time > 200) stars = 1;
    if (stats.collected < stats.total) stars = Math.max(1, stars - 1);
    if (this.vicStars) this.vicStars.textContent = '⭐'.repeat(stars) + '☆'.repeat(3 - stars);

    // Save progress
    const prevStars = saveData.stars?.[this.game.currentLevelId] || 0;
    if (!saveData.stars) saveData.stars = {};
    saveData.stars[this.game.currentLevelId] = Math.max(prevStars, stars);
    if ((saveData.lastLevel || 1) <= this.game.currentLevelId) {
      saveData.lastLevel = Math.min(25, this.game.currentLevelId + 1);
    }
    writeSave(saveData);
  }

  showDefeat() {
    audio.playDefeat();
    this.showScreen('defeat');
  }

  // ── Invulnerability flash ─────────────────────────────────────
  setInvulnFlash(active) {
    this.invulnFlash?.classList.toggle('active', active);
  }

  // ── Toast ─────────────────────────────────────────────────────
  showToast(msg, duration = 2800) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 350);
    }, duration);
  }

  // ── Virtual joystick (touch / mouse) ─────────────────────────
  _setupVirtualJoystick() {
    if (!this.joystickBase) return;
    let active = false;
    let cx = 0, cy = 0;
    const MAX = 42;

    const start = (x, y) => {
      active = true;
      const r = this.joystickBase.getBoundingClientRect();
      cx = r.left + r.width / 2;
      cy = r.top  + r.height / 2;
      move(x, y);
    };
    const move = (x, y) => {
      if (!active) return;
      let dx = x - cx, dy = y - cy;
      const dist = Math.hypot(dx, dy);
      if (dist > MAX) { dx = dx / dist * MAX; dy = dy / dist * MAX; }
      this.joystickStick.style.transform = `translate(${dx}px, ${dy}px)`;
      this.game.input.joystickX = dx / MAX;
      this.game.input.joystickY = dy / MAX;
    };
    const end = () => {
      active = false;
      this.joystickStick.style.transform = 'translate(0px, 0px)';
      this.game.input.joystickX = 0;
      this.game.input.joystickY = 0;
    };

    this.joystickBase.addEventListener('mousedown',  e => start(e.clientX, e.clientY));
    this.joystickBase.addEventListener('touchstart', e => { e.preventDefault(); start(e.touches[0].clientX, e.touches[0].clientY); }, { passive: false });
    window.addEventListener('mousemove',  e => move(e.clientX, e.clientY));
    window.addEventListener('touchmove',  e => { if (active) { e.preventDefault(); move(e.touches[0].clientX, e.touches[0].clientY); } }, { passive: false });
    window.addEventListener('mouseup', end);
    window.addEventListener('touchend', end);
  }
}
