"""
Stussi Launcher — A clean, professional Steam game launcher.
Built with PySide6.
Branding: Navy (#0a1628) · Red (#d42027) · White — F1 / Racing spirit.
Supports Ultra-wide (multi-monitor) setups via centralized content container.
Includes a professional fade-in/fade-out Splash Screen and sound.
"""

import sys
import os
import winsound
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QGridLayout,
    QFrame, QGraphicsDropShadowEffect, QComboBox, QStackedWidget,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Qt, Signal, QThread, QTimer, QObject, QRectF, QPropertyAnimation, QEasingCurve, QRect, Property
)
from PySide6.QtGui import (
    QPixmap, QFont, QColor, QPainter, QPainterPath, QLinearGradient,
    QPen, QIcon, QCursor, QImage,
)

from steam_utils import discover_installed_games, launch_steam_game, format_size, SteamGame

# ─── Paths ───────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    RESOURCE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).parent
else:
    RESOURCE_DIR = Path(__file__).resolve().parent
    APP_DIR = RESOURCE_DIR

LOGO_PATH = str(RESOURCE_DIR / "stussi logo sem fundo.png")
ICON_PATH = str(RESOURCE_DIR / "icon.ico")
CORVETTE_PATH = str(RESOURCE_DIR / "bg_corvette.png")

# ─── Colors ──────────────────────────────────────────────────────────────────

class C:
    NAVY = "#0a1628"
    NAVY_DEEP = "#060d18"
    RED = "#d42027"
    RED_HOVER = "#e8353c"
    RED_DARK = "#a01a1f"
    WHITE = "#ffffff"
    BG = "#0c0c0c"
    BG_GRID = "#0a0a0a"
    CARD_BG = "#161616"
    CARD_BORDER = "#222222"
    CARD_HOVER = "#d42027"
    T1 = "#f0f0f0"
    T2 = "#a0a0a0"
    T3 = "#555555"
    INPUT_BG = "#111111"
    INPUT_BORDER = "#2a2a2a"


# ─── Global QSS ─────────────────────────────────────────────────────────────

QSS = f"""
QMainWindow {{ background-color: {C.BG}; }}
QWidget {{ color: {C.T1}; font-family: "Segoe UI", sans-serif; }}

QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: transparent; width: 5px; border-radius: 2px;
}}
QScrollBar::handle:vertical {{
    background: {C.T3}; min-height: 40px; border-radius: 2px;
}}
QScrollBar::handle:vertical:hover {{ background: {C.RED}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
QScrollBar:horizontal {{ height: 0; }}

QLineEdit {{
    background: {C.INPUT_BG}; border: 1px solid {C.INPUT_BORDER};
    border-radius: 8px; padding: 9px 14px 9px 38px;
    font-size: 13px; color: {C.T1};
    selection-background-color: {C.RED};
}}
QLineEdit:focus {{ border-color: {C.RED}; }}

QComboBox {{
    background: {C.INPUT_BG}; border: 1px solid {C.INPUT_BORDER};
    border-radius: 8px; padding: 8px 14px; font-size: 13px;
    color: {C.T2}; min-width: 140px;
}}
QComboBox:hover {{ border-color: {C.RED}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox::down-arrow {{ image: none; }}
QComboBox QAbstractItemView {{
    background: {C.CARD_BG}; border: 1px solid {C.INPUT_BORDER};
    padding: 4px; selection-background-color: {C.RED};
    color: {C.T1}; outline: none;
}}
"""


# ─── Workers ─────────────────────────────────────────────────────────────────

class _Sig(QObject):
    done = Signal(str, QPixmap)

class ImageWorker(QThread):
    def __init__(self, app_id, url):
        super().__init__()
        self.app_id, self.url = app_id, url
        self.sig = _Sig()

    def run(self):
        try:
            import requests
            r = requests.get(self.url, timeout=8)
            px = QPixmap()
            if r.status_code == 200:
                px.loadFromData(r.content)
            self.sig.done.emit(self.app_id, px)
        except Exception:
            self.sig.done.emit(self.app_id, QPixmap())

class DiscoveryWorker(QThread):
    finished = Signal(list)
    def run(self):
        self.finished.emit(discover_installed_games())


# ─── Game Card (Big Picture Style) ───────────────────────────────────────────

CARD_W, CARD_H = 200, 290
INNER_W, INNER_H = 180, 270

class CardInner(QWidget):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.pixmap = None
        self.hovered = False

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 12, 12)
        p.setClipPath(path)
        
        # Draw Image
        if self.pixmap and not self.pixmap.isNull():
            scaled = self.pixmap.scaled(rect.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (scaled.width() - rect.width()) // 2
            y = (scaled.height() - rect.height()) // 2
            p.drawPixmap(0, 0, scaled.copy(x, y, rect.width(), rect.height()))
        else:
            g = QLinearGradient(0, 0, rect.width(), rect.height())
            hv = hash(self.game.app_id) % 30
            g.setColorAt(0, QColor.fromHsl(215 + hv, 80, 22))
            g.setColorAt(1, QColor.fromHsl(215 + hv, 60, 14))
            p.fillRect(rect, g)
            p.setPen(QColor(255, 255, 255, 190))
            f = QFont("Segoe UI", 16, QFont.Bold)
            p.setFont(f)
            p.drawText(QRectF(rect).adjusted(16, 16, -16, -16), Qt.AlignCenter | Qt.TextWordWrap, self.game.name)
            
        # Draw play overlay on hover or focus
        if self.hovered:
            p.fillRect(rect, QColor(0, 0, 0, 150))
            p.setPen(QColor(255, 255, 255))
            f = QFont("Segoe UI", 48)
            p.setFont(f)
            p.drawText(rect, Qt.AlignCenter, "▶")
            
            # Draw an elegant red border around the card to indicate selection clearly
            p.setClipRect(rect)
            border_pen = QPen(QColor(C.RED))
            border_pen.setWidth(4)
            p.setPen(border_pen)
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(rect), 12, 12)
            
        p.end()

class GameCard(QFrame):
    launch = Signal(str)

    def __init__(self, game: SteamGame, parent=None):
        super().__init__(parent)
        self.game = game
        self.setFixedSize(CARD_W, CARD_H)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setObjectName("gc")
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.inner = CardInner(game)
        self.inner.setParent(self)
        self.inner.setGeometry((CARD_W - INNER_W)//2, (CARD_H - INNER_H)//2, INNER_W, INNER_H)
        
        sh = QGraphicsDropShadowEffect(self.inner)
        sh.setBlurRadius(20)
        sh.setColor(QColor(0, 0, 0, 160))
        sh.setOffset(0, 6)
        self.inner.setGraphicsEffect(sh)
        
        # Animation for resizing inner
        self.anim = QPropertyAnimation(self.inner, b"geometry")
        self.anim.setDuration(120)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        
    def set_image(self, px: QPixmap):
        self.inner.pixmap = px
        self.inner.update()
        
    def _placeholder(self):
        self.inner.update()

    def _set_hover_state(self, active: bool):
        if self.inner.hovered == active:
            return
            
        self.inner.hovered = active
        self.inner.update()
        
        self.anim.stop()
        self.anim.setStartValue(self.inner.geometry())
        if active:
            self.anim.setEndValue(QRect(0, 0, CARD_W, CARD_H))
            fx = self.inner.graphicsEffect()
            fx.setBlurRadius(30)
            fx.setColor(QColor(212, 32, 39, 60)) # Reddish glow on hover/focus
        else:
            self.anim.setEndValue(QRect((CARD_W - INNER_W)//2, (CARD_H - INNER_H)//2, INNER_W, INNER_H))
            fx = self.inner.graphicsEffect()
            fx.setBlurRadius(20)
            fx.setColor(QColor(0, 0, 0, 160))
        self.anim.start()

    def enterEvent(self, e):
        self._set_hover_state(True)
        super().enterEvent(e)

    def leaveEvent(self, e):
        if not self.hasFocus():
            self._set_hover_state(False)
        super().leaveEvent(e)

    def focusInEvent(self, e):
        self._set_hover_state(True)
        super().focusInEvent(e)

    def focusOutEvent(self, e):
        self._set_hover_state(False)
        super().focusOutEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.launch.emit(self.game.app_id)


# ─── Header ─────────────────────────────────────────────────────────────────

class Header(QWidget):
    search_changed = Signal(str)
    sort_changed = Signal(str)
    close_requested = Signal()
    toggle_fs_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(170)
        self._build()

    def _build(self):
        self.setAutoFillBackground(False)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        bar_container = QWidget()
        bar_lay = QHBoxLayout(bar_container)
        bar_lay.setContentsMargins(0, 0, 0, 0)
        bar_lay.setSpacing(0)
        
        bar_lay.addStretch(1)

        self.bar = QWidget()
        self.bar.setMaximumWidth(2560)
        self.bar.setObjectName("headerBar")
        lay = QHBoxLayout(self.bar)
        lay.setContentsMargins(28, 0, 28, 0)
        lay.setSpacing(14)

        self.logo_lbl = QLabel()
        lp = QPixmap(LOGO_PATH)
        if not lp.isNull():
            self.logo_lbl.setPixmap(lp.scaledToHeight(150, Qt.SmoothTransformation))
        self.logo_lbl.setStyleSheet("background:transparent;")
        lay.addWidget(self.logo_lbl)

        lay.addStretch(1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Pesquisar jogos...")
        self.search.setFixedWidth(280)
        self.search.setFixedHeight(36)
        self.search.textChanged.connect(self.search_changed.emit)
        icon = QLabel("🔍")
        icon.setStyleSheet("font-size:13px; background:transparent; padding-left:12px;")
        icon.setParent(self.search)
        icon.move(2, 7)
        lay.addWidget(self.search)

        self.sort = QComboBox()
        self.sort.addItems(["A → Z", "Z → A", "Último jogado", "Tamanho"])
        self.sort.setFixedHeight(36)
        self.sort.currentTextChanged.connect(self.sort_changed.emit)
        lay.addWidget(self.sort)
        
        btn_style = f"""
            QPushButton {{
                background:transparent; border:none; border-radius:18px;
                color:{C.T2}; font-size:18px; font-weight:bold;
            }}
            QPushButton:hover {{
                background:{C.RED}; color:{C.WHITE};
            }}
        """

        self.fs_btn = QPushButton("🗗")
        self.fs_btn.setFixedSize(36, 36)
        self.fs_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.fs_btn.setStyleSheet(btn_style)
        self.fs_btn.setToolTip("Alternar Tela Cheia")
        self.fs_btn.clicked.connect(self.toggle_fs_requested.emit)
        lay.addWidget(self.fs_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        close_btn.setStyleSheet(btn_style)
        close_btn.setToolTip("Fechar")
        close_btn.clicked.connect(self.close_requested.emit)
        lay.addWidget(close_btn)

        bar_lay.addWidget(self.bar, 2)
        bar_lay.addStretch(1)

        root.addWidget(bar_container, 1)

        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet(f"background:{C.RED};")
        root.addWidget(line)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0, QColor(C.NAVY))
        g.setColorAt(1, QColor(C.NAVY_DEEP))
        p.fillRect(self.rect(), g)
        p.end()
        super().paintEvent(e)


# ─── Stats Bar ───────────────────────────────────────────────────────────────

class StatsBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(32, 0, 32, 0)
        lay.setSpacing(14)

        self.count_lbl = QLabel("0 jogos")
        self.count_lbl.setStyleSheet(f"color:{C.T2}; font-size:12px; font-weight:500;")
        dot = QLabel("·")
        dot.setStyleSheet(f"color:{C.RED}; font-size:16px; font-weight:bold;")
        self.size_lbl = QLabel("")
        self.size_lbl.setStyleSheet(f"color:{C.T3}; font-size:12px;")

        lay.addWidget(self.count_lbl)
        lay.addWidget(dot)
        lay.addWidget(self.size_lbl)
        lay.addStretch()

        self.refresh = QPushButton("↻  Atualizar")
        self.refresh.setCursor(QCursor(Qt.PointingHandCursor))
        self.refresh.setFixedHeight(28)
        self.refresh.setStyleSheet(f"""
            QPushButton {{
                background:transparent; border:1px solid {C.INPUT_BORDER};
                border-radius:6px; color:{C.T3}; font-size:11px; padding:0 14px;
            }}
            QPushButton:hover {{
                border-color:{C.RED}; color:{C.RED};
                background:rgba(212,32,39,0.06);
            }}
        """)
        lay.addWidget(self.refresh)

    def update(self, count, total, filtered=False):
        pfx = "Mostrando " if filtered else ""
        suf = "jogo" if count == 1 else "jogos"
        self.count_lbl.setText(f"{pfx}{count} {suf}")
        self.size_lbl.setText(f"{format_size(total)} no disco" if total > 0 else "")


# ─── Empty / Loading states ─────────────────────────────────────────────────

class EmptyState(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(14)
        t = QLabel("Nenhum jogo encontrado")
        t.setStyleSheet(f"color:{C.T1}; font-size:18px; font-weight:600;")
        t.setAlignment(Qt.AlignCenter)
        d = QLabel("Verifique se o Steam está instalado\ne se há jogos na sua biblioteca.")
        d.setStyleSheet(f"color:{C.T3}; font-size:13px;")
        d.setAlignment(Qt.AlignCenter)
        d.setWordWrap(True)
        lay.addWidget(t)
        lay.addWidget(d)

class LoadingState(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(14)
        self._dots = QLabel()
        self._dots.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._dots)
        t = QLabel("Carregando jogos...")
        t.setStyleSheet(f"color:{C.T2}; font-size:14px;")
        t.setAlignment(Qt.AlignCenter)
        lay.addWidget(t)
        self._i = 0
        self._tm = QTimer(self)
        self._tm.timeout.connect(self._tick)
        self._tm.start(350)

    def _tick(self):
        r, g = C.RED, C.T3
        frames = [
            f"<span style='color:{r}'>●</span>  <span style='color:{g}'>●  ●</span>",
            f"<span style='color:{g}'>●</span>  <span style='color:{r}'>●</span>  <span style='color:{g}'>●</span>",
            f"<span style='color:{g}'>●  ●</span>  <span style='color:{r}'>●</span>",
        ]
        self._dots.setText(frames[self._i % 3])
        self._i += 1


# ─── Splash Overlay ─────────────────────────────────────────────────────────

class SplashOverlay(QWidget):
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_opacity = 1.0
        
        self.logo_lbl = QLabel(self)
        lp = QPixmap(LOGO_PATH)
        if not lp.isNull():
            self.logo_lbl.setPixmap(lp.scaledToHeight(300, Qt.SmoothTransformation))
        self.logo_lbl.setAlignment(Qt.AlignCenter)
        self.logo_lbl.setStyleSheet("background: transparent;")
        
        lay = QVBoxLayout(self)
        lay.addWidget(self.logo_lbl)
        
        self.logo_effect = QGraphicsOpacityEffect(self.logo_lbl)
        self.logo_effect.setOpacity(0)
        self.logo_lbl.setGraphicsEffect(self.logo_effect)
        
    def get_bg_opacity(self):
        return self._bg_opacity

    def set_bg_opacity(self, val):
        self._bg_opacity = val
        self.update()

    bg_opacity = Property(float, get_bg_opacity, set_bg_opacity)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(3, 3, 3, int(255 * self._bg_opacity)))
        p.end()
        
    def start(self):
        # Play custom somstussi.wav
        sound_path = RESOURCE_DIR / "somstussi.wav"
        if sound_path.exists():
            winsound.PlaySound(str(sound_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            winsound.PlaySound(r"C:\Windows\Media\Windows Logon.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

        self.anim_in = QPropertyAnimation(self.logo_effect, b"opacity")
        self.anim_in.setDuration(1200)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim_in.finished.connect(self._pause)
        self.anim_in.start()
        
    def _pause(self):
        QTimer.singleShot(4000, self._fade_out_logo)
        
    def _fade_out_logo(self):
        self.anim_out_logo = QPropertyAnimation(self.logo_effect, b"opacity")
        self.anim_out_logo.setDuration(800)
        self.anim_out_logo.setStartValue(1.0)
        self.anim_out_logo.setEndValue(0.0)
        self.anim_out_logo.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim_out_logo.finished.connect(self._fade_out_overlay)
        self.anim_out_logo.start()
        
    def _fade_out_overlay(self):
        self.anim_out = QPropertyAnimation(self, b"bg_opacity")
        self.anim_out.setDuration(1000)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim_out.finished.connect(self._done)
        self.anim_out.start()
        
    def _done(self):
        self.hide()
        if hasattr(self.parent(), 'splash'):
            self.parent().splash = None
        self.deleteLater()


# ─── Main Window ─────────────────────────────────────────────────────────────

class StussiLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stussi Launcher")
        self.setMinimumSize(900, 600)
        self._is_fs = True
        
        self.games: list[SteamGame] = []
        self.cards: dict[str, GameCard] = {}
        self.workers: list[ImageWorker] = []
        self._filter = ""
        self._sort = "A → Z"

        self._make_icon()
        self.setStyleSheet(QSS)
        self._build_ui()
        
        # Setup splash screen
        self.splash = SplashOverlay(self)
        self.splash.resize(1180, 740)
        
        self._apply_fullscreen()
        self.splash.start()
        self._discover()

    def _apply_fullscreen(self):
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screens = QApplication.screens()
        tr = screens[0].geometry()
        for s in screens[1:]:
            tr = tr.united(s.geometry())
        self.setGeometry(tr)
        self.show()
        if getattr(self, 'splash', None) is not None and self.splash.isVisible():
            self.splash.setGeometry(0, 0, tr.width(), tr.height())
            self.splash.raise_()
        self.header.fs_btn.setText("🗗")
        if hasattr(self.header, 'bar'):
            self.header.bar.setMaximumWidth(2560)
        self.central_container.setMaximumWidth(2560)

    def _apply_windowed(self):
        self.setWindowFlags(Qt.Window)
        self.showNormal()
        self.resize(1280, 800)
        if getattr(self, 'splash', None) is not None and self.splash.isVisible():
            self.splash.setGeometry(0, 0, self.width(), self.height())
            self.splash.raise_()
        self.header.fs_btn.setText("⛶")
        if hasattr(self.header, 'bar'):
            self.header.bar.setMaximumWidth(16777215)
        self.central_container.setMaximumWidth(16777215)

    def _make_icon(self):
        # Prefer a real .ico file if it exists; otherwise fall back to the logo.
        if Path(ICON_PATH).is_file():
            self.setWindowIcon(QIcon(ICON_PATH))
            return

        logo = QPixmap(LOGO_PATH)
        if not logo.isNull():
            s = 256
            ico = QPixmap(s, s)
            ico.fill(QColor(C.NAVY))
            p = QPainter(ico)
            p.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, s, s), 36, 36)
            p.setClipPath(path)
            p.fillRect(0, 0, s, s, QColor(C.NAVY))
            p.fillRect(0, s - 12, s, 12, QColor(C.RED))
            sc = logo.scaled(s - 32, s - 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            p.drawPixmap((s - sc.width()) // 2, (s - 12 - sc.height()) // 2, sc)
            p.end()
            self.setWindowIcon(QIcon(ico))

    def _build_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        
        main_vbox = QVBoxLayout(cw)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)
        
        self.header = Header()
        self.header.search_changed.connect(self._on_search)
        self.header.sort_changed.connect(self._on_sort)
        self.header.close_requested.connect(self.close)
        self.header.toggle_fs_requested.connect(self._toggle_fullscreen)
        main_vbox.addWidget(self.header)
        
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        outer_layout.addStretch(1)
        
        self.central_container = QWidget()
        self.central_container.setMaximumWidth(2560)
        
        ml = QVBoxLayout(self.central_container)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        self.stats = StatsBar()
        self.stats.refresh.clicked.connect(self._refresh)
        ml.addWidget(self.stats)

        self.stack = QStackedWidget()
        self.loading = LoadingState()
        self.empty = EmptyState()
        self.stack.addWidget(self.loading)
        self.stack.addWidget(self.empty)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFocusPolicy(Qt.NoFocus)

        self.grid_w = QWidget()
        self.grid_w.setStyleSheet("background:transparent;")
        self.grid = QGridLayout(self.grid_w)
        self.grid.setContentsMargins(32, 20, 32, 32)
        self.grid.setSpacing(18)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll.setWidget(self.grid_w)
        self.stack.addWidget(self.scroll)

        ml.addWidget(self.stack, 1)
        self.stack.setCurrentWidget(self.loading)
        
        outer_layout.addWidget(self.central_container, 2)
        outer_layout.addStretch(1)
        
        main_vbox.addLayout(outer_layout, 1)

    def _toggle_fullscreen(self):
        if self._is_fs:
            self._is_fs = False
            self._apply_windowed()
        else:
            self._is_fs = True
            self._apply_fullscreen()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw dark corvette background covering the entire window
        cv_pixmap = QPixmap(LOGO_PATH)
        if not cv_pixmap.isNull():
            scaled_cv = cv_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            cx = (scaled_cv.width() - self.width()) // 2
            cy = (scaled_cv.height() - self.height()) // 2
            p.drawPixmap(0, 0, scaled_cv.copy(cx, cy, self.width(), self.height()))
            # Add a dark overlay to ensure content is readable and professional
            p.fillRect(self.rect(), QColor(0, 0, 0, 180))
        else:
            g_bg = QLinearGradient(0, 0, 0, self.height())
            g_bg.setColorAt(0.0, QColor("#0e0e0e"))
            g_bg.setColorAt(1.0, QColor("#030303"))
            p.fillRect(self.rect(), g_bg)

        # Draw the logo watermark in the games area
        bg_pixmap = QPixmap(LOGO_PATH)
        if not bg_pixmap.isNull():
            games_area_y = 170
            games_area_h = self.height() - games_area_y
            max_w = int(self.width() * 0.4)
            max_h = int(games_area_h * 0.7)
            
            scaled = bg_pixmap.scaled(max_w, max_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x_offset = (self.width() - scaled.width()) // 2
            y_offset = games_area_y + (games_area_h - scaled.height()) // 2
            
            p.setOpacity(0.06)
            p.drawPixmap(x_offset, y_offset, scaled)
            p.setOpacity(1.0)

        p.end()
        super().paintEvent(e)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if getattr(self, 'splash', None) is not None:
            try:
                if self.splash.isVisible():
                    self.splash.setGeometry(self.rect())
            except RuntimeError:
                self.splash = None
            
        if self.games and self.stack.currentWidget() == self.scroll:
            if not hasattr(self, '_rt'):
                self._rt = QTimer(self)
                self._rt.setSingleShot(True)
                self._rt.timeout.connect(self._relayout)
            self._rt.start(120)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
            return
            
        if e.key() == Qt.Key_F11:
            self._toggle_fullscreen()
            return

        focused = QApplication.focusWidget()
        if not isinstance(focused, GameCard):
            if e.key() in (Qt.Key_Down, Qt.Key_Right):
                games = self._sorted()
                if games:
                    self.cards[games[0].app_id].setFocus()
            super().keyPressEvent(e)
            return
            
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            focused.launch.emit(focused.game.app_id)
            return

        games = self._sorted()
        app_ids = [g.app_id for g in games]
        try:
            idx = app_ids.index(focused.game.app_id)
        except ValueError:
            return

        cols = max(1, (self.grid_w.width() - 64) // (CARD_W + 18))
        new_idx = idx

        if e.key() == Qt.Key_Right:
            new_idx = idx + 1
        elif e.key() == Qt.Key_Left:
            new_idx = idx - 1
        elif e.key() == Qt.Key_Down:
            new_idx = idx + cols
        elif e.key() == Qt.Key_Up:
            new_idx = idx - cols

        if 0 <= new_idx < len(games):
            card = self.cards[games[new_idx].app_id]
            card.setFocus()
            self.scroll.ensureWidgetVisible(card)
        else:
            super().keyPressEvent(e)

    def _discover(self):
        self.dw = DiscoveryWorker()
        self.dw.finished.connect(self._on_discovered)
        self.dw.start()

    def _on_discovered(self, games):
        self.games = games
        if not games:
            self.stack.setCurrentWidget(self.empty)
            self.stats.update(0, 0)
            return
        self._populate()
        self.stack.setCurrentWidget(self.scroll)
        self.stats.update(len(games), sum(g.size_on_disk for g in games))
        self._load_images()

    def _sorted(self):
        g = self.games
        if self._filter:
            q = self._filter.lower()
            g = [x for x in g if q in x.name.lower()]
        key_map = {
            "A → Z": lambda x: x.name.lower(),
            "Z → A": lambda x: x.name.lower(),
            "Último jogado": lambda x: x.last_played,
            "Tamanho": lambda x: x.size_on_disk,
        }
        rev = self._sort in ("Z → A", "Último jogado", "Tamanho")
        g.sort(key=key_map.get(self._sort, lambda x: x.name.lower()), reverse=rev)
        return g

    def _populate(self):
        self._clear()
        games = self._sorted()
        cols = max(1, (self.grid_w.width() - 64) // (CARD_W + 18))
        for i, game in enumerate(games):
            c = GameCard(game)
            c.launch.connect(self._launch)
            c._placeholder()
            self.grid.addWidget(c, i // cols, i % cols)
            self.cards[game.app_id] = c
        self.stats.update(len(games), sum(x.size_on_disk for x in games), bool(self._filter))

    def _clear(self):
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w:
                w.deleteLater()
        self.cards.clear()

    def _load_images(self):
        for g in self.games:
            w = ImageWorker(g.app_id, g.capsule_image_url)
            w.sig.done.connect(self._on_img)
            self.workers.append(w)
            w.start()

    def _on_img(self, aid, px):
        if aid in self.cards:
            self.cards[aid].set_image(px)

    def _on_search(self, t):
        self._filter = t.strip()
        self._populate()

    def _on_sort(self, t):
        self._sort = t
        self._populate()

    def _launch(self, aid):
        launch_steam_game(aid)

    def _refresh(self):
        self.workers.clear()
        self._clear()
        self.stack.setCurrentWidget(self.loading)
        self._discover()

    def _relayout(self):
        games = self._sorted()
        cols = max(1, (self.grid_w.width() - 64) // (CARD_W + 18))
        for i, g in enumerate(games):
            if g.app_id in self.cards:
                c = self.cards[g.app_id]
                self.grid.removeWidget(c)
                self.grid.addWidget(c, i // cols, i % cols)


# ─── Entry ───────────────────────────────────────────────────────────────────

def add_to_startup():
    try:
        import winreg
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(sys.argv[0])
            
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "StussiLauncher", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Failed to add to startup: {e}")

def main():
    add_to_startup()
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    if Path(ICON_PATH).is_file():
        app.setWindowIcon(QIcon(ICON_PATH))
    w = StussiLauncher()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
