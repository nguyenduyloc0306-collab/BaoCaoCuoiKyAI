
# ----------------------------------------------------------------------------
# MAU SAC (Tone tron, hien dai, theme toi - "flat dark UI")
# ----------------------------------------------------------------------------
COLOR_BG           = (18, 20, 28)        # nen chinh
COLOR_PANEL        = (26, 29, 40)        # nen panel / sidebar
COLOR_PANEL_LIGHT  = (36, 40, 55)        # card / input box
COLOR_PANEL_BORDER = (55, 60, 80)        # vien ngoai panel/card
COLOR_GRID_LINE    = (42, 46, 62)        # duong ke luoi
COLOR_GRID_CELL    = (24, 27, 36)        # o trong

COLOR_OBSTACLE        = (80, 86, 104)
COLOR_OBSTACLE_BORDER = (110, 116, 136)

COLOR_TEXT        = (235, 238, 248)      # chu chinh - sang hon
COLOR_TEXT_DIM    = (155, 162, 182)      # chu phu
COLOR_TEXT_ACCENT = (255, 255, 255)

COLOR_ACCENT      = (100, 180, 255)      # xanh duong accent
COLOR_ACCENT_DARK = (62, 122, 196)
COLOR_ACCENT_GLOW = (60, 140, 230)
COLOR_SUCCESS     = (100, 215, 150)      # xanh la
COLOR_DANGER      = (240, 100, 100)      # do
COLOR_WARNING     = (240, 185, 80)       # vang

COLOR_BUTTON        = (46, 51, 70)
COLOR_BUTTON_HOVER  = (62, 68, 92)
COLOR_BUTTON_BORDER = (72, 78, 104)
COLOR_BUTTON_ACTIVE = (100, 180, 255)
COLOR_BUTTON_TEXT   = (220, 224, 238)

# Bang mau rieng cho tung agent (toi da 8 hunter + 8 runner phan biet)
HUNTER_PALETTE = [
    (235, 95, 95),    # do
    (235, 140, 60),   # cam
    (200, 80, 160),   # hong-tim
    (180, 60, 60),    # do dam
    (220, 120, 40),
    (160, 40, 120),
    (210, 90, 110),
    (170, 70, 70),
]
RUNNER_PALETTE = [
    (95, 200, 140),   # xanh la
    (90, 169, 255),   # xanh duong
    (150, 210, 90),   # xanh chuoi
    (80, 200, 200),   # xanh ngoc
    (110, 160, 240),
    (100, 220, 170),
    (60, 180, 220),
    (130, 200, 110),
]

# ----------------------------------------------------------------------------
# KICH THUOC MAN HINH / LAYOUT
# ----------------------------------------------------------------------------
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
FPS = 60

SIDEBAR_WIDTH = 330          # panel ben phai: dieu khien + log
TOPBAR_HEIGHT = 52           # thanh tren cung trong man hinh choi
BOARD_MARGIN = 16            # le quanh ban co

MIN_GRID_SIZE = 5
MAX_GRID_SIZE = 40
DEFAULT_GRID_SIZE = 20

MIN_CELL_PX = 10              # kich thuoc o nho nhat khi grid lon

# ----------------------------------------------------------------------------
# TOC DO / VONG CHOI
# ----------------------------------------------------------------------------
DEFAULT_MAX_STEPS = 200
MIN_MAX_STEPS = 20
MAX_MAX_STEPS = 2000

DEFAULT_STEP_INTERVAL_MS = 250   # thoi gian giua 2 buoc (auto-run), ms
MIN_STEP_INTERVAL_MS = 30
MAX_STEP_INTERVAL_MS = 1000

DEFAULT_OBSTACLE_DENSITY = 0.15  # 15% so o la vat can khi sinh ngau nhien

# ----------------------------------------------------------------------------
# DANH SACH THUAT TOAN (key noi bo -> ten hien thi)
# ----------------------------------------------------------------------------
ALGORITHMS = [
    ("bfs", "BFS"),
    ("dfs", "DFS"),
    ("greedy", "Greedy Best-First Search"),
    ("astar", "A*"),
    ("local_beam", "Local Beam Search"),
    ("hill_climbing", "Hill Climbing"),
    ("backtracking", "Backtracking Search"),
    ("forward_checking", "Forward Checking"),
    ("sensorless", "Sensorless Search"),
    ("and_or", "AND-OR Graph Search"),
    ("minimax", "Minimax"),
    ("alpha_beta", "Alpha-Beta Pruning"),
]
ALGORITHM_KEYS = [a[0] for a in ALGORITHMS]
ALGORITHM_LABELS = {k: v for k, v in ALGORITHMS}

# Nhan rut gon (dung trong cac khung UI hep, vi du card agent trong menu setup)
ALGORITHM_SHORT_LABELS = {
    "bfs": "BFS",
    "dfs": "DFS",
    "greedy": "Greedy BFS",
    "astar": "A*",
    "local_beam": "Local Beam",
    "hill_climbing": "Hill Climb",
    "backtracking": "Backtrack",
    "forward_checking": "Fwd Check",
    "sensorless": "Sensorless",
    "and_or": "AND-OR",
    "minimax": "Minimax",
    "alpha_beta": "Alpha-Beta",
}

DEFAULT_HUNTER_ALGO = "astar"
DEFAULT_RUNNER_ALGO = "greedy"

# Thuat toan can do sau tim kiem (gioi han de tranh no to hop)
MINIMAX_DEPTH = 4
ALPHA_BETA_DEPTH = 6

# Hill Climbing
HC_RESTARTS = 4

# Local Beam Search
LOCAL_BEAM_WIDTH = 6
LOCAL_BEAM_ITERATIONS = 10

# Ban kinh "tam nhin" / vung xet ung vien khi mo phong cac thuat toan tim duong
# duoc dung theo kieu "chon huong" (Runner tron, Hunter duoi tu xa)
SEARCH_HORIZON = 999  # khong gioi han: luon tinh tren toan grid (grid khong qua lon)
