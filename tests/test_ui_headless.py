"""
test_ui_headless.py
Dung pygame STUB (khong ve thuc) de mo phong toan bo luong tuong tac UI:
- Khoi tao Application
- O man hinh Setup: keo slider, doi che do placement, ve vat can, them/xoa
  agent, doi thuat toan, dat vi tri tuy chinh, bam Bat dau
- Sang man hinh Playing: chay nhieu step, bam Pause/Resume, doi speed,
  bam Restart, bam Menu de quay lai Setup
- Kiem tra khong co exception nao xay ra trong toan bo qua trinh.

CHAY: PYTHONPATH=/home/claude/pg_stub:. python3 test_ui_headless.py
"""
import os
import sys
sys.path.insert(0, "/home/claude/pg_stub")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame  # se load tu stub vi duoc chen vao dau sys.path
import config
from main import Application, STATE_SETUP, STATE_PLAYING


def make_event(type_, **kwargs):
    return pygame.Event(type_, **kwargs)


def test_full_flow():
    print("=== Khoi tao Application ===")
    app = Application()
    assert app.state == STATE_SETUP
    print("OK - state =", app.state)

    setup = app.setup_screen

    print("\n=== Keo slider grid size ===")
    app._handle_playing_event  # chi de kiem ton tai, khong goi
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=(setup.slider_grid.rect.x + 10, setup.slider_grid.rect.centery), button=1)
    setup.handle_event(ev)
    print("OK - grid_size sau keo:", setup.grid_size)

    print("\n=== Doi che do placement sang Custom ===")
    custom_rect = setup.segment_placement._item_rects[1]
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=custom_rect.center, button=1)
    setup.handle_event(ev)
    assert setup.placement_mode == "custom"
    print("OK - placement_mode =", setup.placement_mode)

    print("\n=== Bat cong cu ve vat can va click 1 o tren board ===")
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=setup.btn_paint_obstacle.rect.center, button=1)
    setup.handle_event(ev)
    assert setup.active_tool == "obstacle"
    board_cell_pixel = setup.board_renderer.cell_center(3, 3)
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=board_cell_pixel, button=1)
    setup.handle_event(ev)
    print("OK - obstacle tai (3,3):", setup.grid.is_obstacle(3, 3))

    # tat cong cu ve vat can lai
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=setup.btn_paint_obstacle.rect.center, button=1)
    setup.handle_event(ev)
    assert setup.active_tool == "none"

    print("\n=== Them 1 Hunter va 1 Runner ===")
    n_h_before = len(setup.hunter_configs)
    n_r_before = len(setup.runner_configs)
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=setup.btn_add_hunter.rect.center, button=1)
    setup.handle_event(ev)
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=setup.btn_add_runner.rect.center, button=1)
    setup.handle_event(ev)
    assert len(setup.hunter_configs) == n_h_before + 1
    assert len(setup.runner_configs) == n_r_before + 1
    print("OK - so hunter:", len(setup.hunter_configs), " so runner:", len(setup.runner_configs))

    print("\n=== Doi thuat toan cua Hunter 1 (next x3) ===")
    row = setup._agent_rows[0]
    old_algo = row["config"].algo_key
    for _ in range(3):
        ev = make_event(pygame.MOUSEBUTTONDOWN, pos=row["algo_next_rect"].center, button=1)
        setup.handle_event(ev)
    print("OK - algo doi tu", old_algo, "->", row["config"].algo_key)

    print("\n=== Dat vi tri tuy chinh cho Hunter 1 ===")
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=row["place_btn"].rect.center, button=1)
    setup.handle_event(ev)
    assert setup.active_tool == "place_agent"
    target_cell_pixel = setup.board_renderer.cell_center(1, 1)
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=target_cell_pixel, button=1)
    setup.handle_event(ev)
    print("OK - vi tri Hunter 1:", row["config"].pos)

    print("\n=== Random vi tri tat ca ===")
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=setup.btn_random_positions.rect.center, button=1)
    setup.handle_event(ev)
    all_positions = [c.pos for c in setup.hunter_configs + setup.runner_configs]
    assert all(p is not None for p in all_positions)
    assert len(set(all_positions)) == len(all_positions)
    print("OK - tat ca vi tri hop le va khong trung:", all_positions)

    print("\n=== Bam BAT DAU TRAN DAU ===")
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=setup.btn_start.rect.center, button=1)
    started = setup.handle_event(ev)
    assert started is True
    app._start_match()
    assert app.state == STATE_PLAYING
    print("OK - state =", app.state, " so agent trong engine:", len(app.engine.agents))

    print("\n=== Chay 30 step lien tuc (giong auto-run) ===")
    for i in range(30):
        app._advance_one_step()
        if app.engine.is_finished():
            print(f"   Game ket thuc o step {app.engine.step_count}, ket qua: {app.engine.result}")
            break
    print("OK - chay step khong loi.")

    print("\n=== Bam Pause / Resume ===")
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=app.hud.btn_pause.rect.center, button=1)
    app._handle_playing_event(ev)
    print("OK - paused =", app.paused)
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=app.hud.btn_pause.rect.center, button=1)
    app._handle_playing_event(ev)
    print("OK - paused =", app.paused)

    print("\n=== Keo slider toc do ===")
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=(app.hud.speed_slider.rect.right - 5, app.hud.speed_slider.rect.centery), button=1)
    app._handle_playing_event(ev)
    print("OK - step_interval_ms =", app.step_interval_ms)

    print("\n=== Bam Choi lai (Restart) ===")
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=app.hud.btn_restart.rect.center, button=1)
    app._handle_playing_event(ev)
    assert app.state == STATE_PLAYING
    assert app.engine.step_count == 0
    print("OK - tran moi step_count =", app.engine.step_count)

    print("\n=== Bam Menu (quay lai Setup) ===")
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=app.hud.btn_back.rect.center, button=1)
    app._handle_playing_event(ev)
    assert app.state == STATE_SETUP
    print("OK - state =", app.state)

    print("\n=== Goi _draw() o ca 2 state (kiem tra khong loi khi ve) ===")
    app.state = STATE_SETUP
    app._draw()
    app.state = STATE_PLAYING
    app._draw()
    print("OK - _draw() khong loi.")

    print("\n>>> TOAN BO LUONG UI HOAT DONG KHONG LOI (voi pygame stub).")


def test_grid_resize_then_start():
    print("\n=== Test doi kich thuoc grid lien tuc nhieu lan roi bat dau tran ===")
    app = Application()
    setup = app.setup_screen
    for size in [5, 10, 35, 8]:
        setup._on_grid_size_change(size)
    setup._randomize_all_positions()
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=setup.btn_start.rect.center, button=1)
    started = setup.handle_event(ev)
    assert started is True
    app._start_match()
    assert app.engine.grid.width == 8
    print("OK - grid cuoi cung =", app.engine.grid.width, "x", app.engine.grid.height)


def test_remove_all_but_one_agent():
    print("\n=== Test khong the xoa agent cuoi cung ===")
    app = Application()
    setup = app.setup_screen
    assert len(setup.hunter_configs) == 1
    setup._remove_agent("hunter", 0)
    assert len(setup.hunter_configs) == 1  # khong duoc xoa, van con 1
    print("OK - khong xoa duoc hunter cuoi cung, message:", setup.message)


def test_agent_list_scroll():
    print("\n=== Test cuon danh sach agent khi co nhieu agent (vuot qua khung nhin) ===")
    app = Application()
    setup = app.setup_screen

    # them toi da agent de chac chan vuot qua vung hien thi va can cuon
    for _ in range(7):
        setup._add_hunter()
    for _ in range(7):
        setup._add_runner()
    assert len(setup.hunter_configs) == 8
    assert len(setup.runner_configs) == 8
    assert setup.agent_scroll.needs_scroll(), "Voi 16 agent phai can cuon"
    print("OK - content_height:", setup.agent_scroll.content_height,
          " visible_height:", setup.agent_scroll.rect.height,
          " max_offset:", setup.agent_scroll.max_offset())

    # --- test lan chuot (MOUSEWHEEL) ---
    old_offset = setup.agent_scroll.offset
    wheel_pos = setup.agent_scroll.rect.center
    pygame.mouse._pos = wheel_pos
    ev = make_event(pygame.MOUSEWHEEL, y=-3, pos=wheel_pos)
    setup.handle_event(ev)
    assert setup.agent_scroll.offset > old_offset, "Lan chuot xuong phai tang offset"
    print("OK - sau lan chuot xuong, offset:", setup.agent_scroll.offset)

    # --- test keo thanh scrollbar truc tiep toi cuoi ---
    bar_rect = setup.agent_scroll._bar_geometry()
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=bar_rect.center, button=1)
    setup.handle_event(ev)
    ev = make_event(pygame.MOUSEMOTION, pos=(bar_rect.centerx, setup.agent_scroll.rect.bottom), button=1)
    setup.handle_event(ev)
    assert setup.agent_scroll.offset == setup.agent_scroll.max_offset()
    print("OK - keo scrollbar xuong day, offset:", setup.agent_scroll.offset,
          " == max_offset:", setup.agent_scroll.max_offset())

    # --- sau khi cuon toi day, dong agent CUOI CUNG phai nam trong vung nhin
    #     thay va co the bam nut "Dat" cua no ---
    setup._sync_agent_row_positions()
    last_row = setup._agent_rows[-1]
    visible_rect = pygame.Rect(
        setup.sidebar_rect.x, setup.agent_list_top,
        setup.sidebar_rect.width, setup.agent_list_bottom - setup.agent_list_top,
    )
    assert last_row["_visible_y"] + 58 <= visible_rect.bottom + 4, \
        "Dong cuoi cung phai nam trong vung nhin sau khi cuon het"
    print("OK - dong agent cuoi cung da hien trong khung nhin sau khi cuon, y =",
          last_row["_visible_y"])

    # --- bam nut Dat cua dong cuoi (gio da o trong vung nhin) phai hoat dong ---
    setup._on_placement_mode_change("custom")
    ev = make_event(pygame.MOUSEBUTTONDOWN, pos=last_row["place_btn"].rect.center, button=1)
    setup.handle_event(ev)
    assert setup.active_tool == "place_agent"
    assert setup.tool_target_index == (last_row["role"], last_row["index"])
    print("OK - bam nut 'Dat' cua dong da cuon toi hoat dong dung agent:",
          setup.tool_target_index)

    # --- cuon nguoc len dau bang lan chuot ---
    ev = make_event(pygame.MOUSEWHEEL, y=20, pos=wheel_pos)
    setup.handle_event(ev)
    assert setup.agent_scroll.offset == 0.0
    print("OK - lan chuot len nhieu dua offset ve 0.")

    print(">>> TEST SCROLL DANH SACH AGENT PASS.")


if __name__ == "__main__":
    test_full_flow()
    test_grid_resize_then_start()
    test_remove_all_but_one_agent()
    test_agent_list_scroll()
    print("\n>>> TAT CA TEST UI HEADLESS PASS.")
