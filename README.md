# AI Hunter vs Runner

Game mo phong truy bat tren luoi (grid) giua hai phe: **Hunter** (ke san moi -
muc tieu: bat duoc Runner) va **Runner** (ke bi san - muc tieu: song sot den
het so buoc quy dinh). Moi agent co the dung mot trong 12 thuat toan AI khac
nhau, co the them nhieu Hunter/Runner, tuy chinh vi tri bat dau va vat can.

## Cai dat

Yeu cau Python 3.9+.

```bash
pip install -r requirements.txt
```

## Chay

```bash
python3 main.py
```

## Cach choi

1. **Man hinh Thiet lap**:
   - Chinh kich thuoc ban do, so buoc toi da, mat do vat can ngau nhien
     bang cac thanh truot ben trai.
   - Bam "Sinh ngau" de sinh vat can ngau nhien theo mat do da chon,
     hoac "Xoa het vat can" de lam sach ban do.
   - Chon che do vi tri bat dau: Ngau nhien (tu dong random khi bat dau
     tran) hoac Tu chon - click (tu ve vat can / dat vi tri agent bang
     tay tren ban do xem truoc ben phai).
   - O che do "Tu chon", bam nut "Cong cu: Ve vat can" de bat/tat che do
     ve vat can bang chuot (click hoac keo chuot tren ban do).
   - Voi moi agent trong danh sach: dung mui ten "<" ">" de doi thuat
     toan AI, bam "Dat" roi click vao ban do de dat vi tri rieng, bam
     "x" de xoa agent do.
   - Bam "+ Hunter" / "+ Runner" de them agent moi (toi da 8 moi
     loai). Bam "Random vi tri tat ca" de tu dong xep vi tri khong
     trung nhau.
   - Bam "BAT DAU TRAN DAU" de vao tran.

2. **Man hinh Choi**:
   - Tran tu dong chay theo thoi gian thuc; dung phim Space hoac nut
     "Tam dung" de dung/tiep tuc.
   - Keo thanh "Tre giua buoc" de chinh toc do (gia tri nho hon = chay
     nhanh hon).
   - Bam "Choi lai" de choi lai tran voi cung cau hinh (vi tri se duoc
     random lai neu dang o che do Ngau nhien).
   - Bam "Menu" hoac phim Esc de quay lai man hinh thiet lap va
     chinh sua cau hinh.
   - Hinh thoi (kim cuong) = Hunter, hinh tron = Runner. So trong moi agent
     la ID rieng. Khi Runner bi bat (cung o voi Hunter), Runner bien mat va
     co hieu ung vong tron do lan ra.

## Luat choi

- **Runner thang**: con it nhat 1 Runner song sot khi het so buoc toi da.
- **Hunter thang**: tat ca Runner deu bi bat (cung o voi mot Hunter bat ky)
  truoc khi het buoc.

## Cac thuat toan AI ho tro

| Nhom | Thuat toan |
|---|---|
| Tim kiem mu | BFS, DFS |
| Tim kiem co thong tin | Greedy Best-First Search, A* |
| Tim kiem cuc bo | Local Beam Search, Hill Climbing |
| CSP (rang buoc) | Backtracking Search, Forward Checking |
| Moi truong khong xac dinh / khong quan sat | Sensorless Search, AND-OR Graph Search |
| Doi khang (game tree) | Minimax, Alpha-Beta Pruning |

**Nguyen tac thiet ke chung:**
- **Voi Hunter** (BFS/DFS/Greedy/A*): tinh duong di toi Runner gan nhat va
  di buoc dau tien tren duong do.
- **Voi Runner** (BFS/DFS/Greedy/A*): cung thuat toan duoc "lat vai" - dung
  de DO khoang cach thuc (qua duong di, co tinh vat can) tu cac o lan can
  toi Hunter gan nhat, roi chon huong co khoang cach lon nhat (chien luoc
  tron thuan, khong huong toi 1 dich cu the).
- **Local Beam Search / Hill Climbing**: toi uu hoa mot "ke hoach" gom
  nhieu buoc di lien tiep theo ham muc tieu khoang cach (Hunter toi thieu
  hoa, Runner toi da hoa), roi chi thuc hien buoc dau tien cua ke hoach tot
  nhat tim duoc (kieu Model Predictive Control). Local Beam Search giu k
  ke hoach song song va chon lai k ke hoach tot nhat moi vong lap; Hill
  Climbing chi giu 1 ke hoach, dung random-restart de tranh ket cuc tri
  dia phuong.
- **Backtracking Search / Forward Checking**: mo hinh CSP thuc su - bien la
  huong di tai tung buoc trong 1 ke hoach K buoc, mien gia tri la 4 huong,
  rang buoc la "khong vao vat can/ra bien" va "khong tu nop minh" (cho
  Runner). Backtracking gan tung bien va quay lui khi vi pham rang buoc;
  Forward Checking them buoc kiem tra truoc mien gia tri cua bien tiep
  theo de cat nhanh that bai SOM hon.
- **Sensorless Search**: agent KHONG dung vi tri chinh xac cua doi phuong,
  chi duy tri mot "belief state" (tap hop vi tri co the, lan rong dan theo
  thoi gian) va chon nuoc di toi uu cho TRUONG HOP XAU NHAT trong belief
  state do.
- **AND-OR Graph Search**: coi doi phuong la "moi truong khong xac dinh" -
  sau moi buoc cua agent (OR-node, agent duoc chon), doi phuong duoc gia
  dinh CO THE di toi BAT KY huong nao (AND-node, phai an toan/toi voi MOI
  kha nang), khac voi Minimax la doi thu CHU DONG chon nuoc xau nhat.
- **Minimax / Alpha-Beta Pruning**: tim kiem cay game doi khang THAT giua
  agent dang xet va doi thu gan nhat cua no, voi do sau gioi han va ham
  danh gia la khoang cach (co tinh vat can qua ban do BFS-distance).

## Cau truc du an

```
ai_hunter_runner/
├── main.py                       # Entry point, game loop, quan ly man hinh
├── config.py                     # Hang so: mau sac, kich thuoc, danh sach thuat toan
├── grid.py                       # Lop Grid: vat can, kiem tra hop le
├── agent.py                      # Lop Agent (Hunter/Runner)
├── game_engine.py                # Trang thai tran dau, luat thang/thua
├── utils.py                      # Ham dung chung (khoang cach, hang xom...)
├── algorithms/
│   ├── search_uninformed.py      # BFS, DFS
│   ├── search_informed.py        # Greedy Best-First Search, A*
│   ├── local_search.py           # Hill Climbing, Local Beam Search
│   ├── csp_search.py             # Backtracking Search, Forward Checking
│   ├── belief_search.py          # Sensorless Search, AND-OR Graph Search
│   └── adversarial.py            # Minimax, Alpha-Beta Pruning
└── ui/
    ├── widgets.py                 # Button, Slider, SegmentedControl...
    ├── renderer.py                # Ve ban co, vat can, agent
    ├── hud.py                     # Panel dieu khien trong man hinh choi
    └── menu.py                    # Man hinh thiet lap truoc tran
```

## Tuy chinh them

Cac hang so quan trong (do sau Minimax/Alpha-Beta, do sau AND-OR, do rong
beam cua Local Beam Search, so buoc ke hoach CSP...) deu nam trong
config.py va dau file thuat toan tuong ung, co the chinh truc tiep de thay
doi do "thong minh" / toc do tinh toan cua tung thuat toan.
