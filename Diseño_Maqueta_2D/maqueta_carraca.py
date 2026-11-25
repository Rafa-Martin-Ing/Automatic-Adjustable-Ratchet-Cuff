"""
Maqueta plana del agarre con carraca (variante 5b) para montar sobre una tabla.
Genera un STEP con cada pieza como sólido independiente (importable en Onshape).

Unidades: mm. Plano de la maqueta = XY, espesor en Z. La cara superior del tablero es Z = 0.
Pivote principal en el origen. Posición dibujada = palas CERRADAS (θ = 0).
La pala móvil (superior) abre girando en sentido antihorario (+Z) alrededor del pivote.

Parámetros principales arriba: cámbialos y vuelve a ejecutar.
"""
import math
import cadquery as cq

# ---------------- parámetros ----------------
T = 6.0                 # espesor de las piezas impresas/cortadas
GAP = 1.0               # arandela entre capas
ZA = GAP                # capa A: pala móvil, trinquete, piñón
ZB = ZA + T + GAP       # capa B: pala fija (encima)

C = (125.0, 0.0)        # centro del agarre (antebrazo)
R_SH0, R_SH1 = 52.0, 62.0   # carcasa de las palas (radio interior/exterior)
R_PAD0 = 46.0               # interior del acolchado de EVA (6 mm)
ARC_MOV = (0.30, 2.30)      # rad, pala móvil (arriba)
ARC_FIX = (-2.65, -0.30)    # rad, pala fija (abajo)
ARM_W = 18.0

# carraca (en la pala móvil)
RR, RH, NT = 36.0, 4.5, 30          # radio de fondo, altura de diente, nº de dientes (12°)
PITCH = 2 * math.pi / NT

# engranajes: sector en la pala móvil + piñón en el stepper
MOD = 1.5
BACKLASH = 0.25                      # juego entre dientes (mm), para impresión
Z_SECT = 92                          # dientes si fuese rueda completa
Z_PIN = 14
SECT_SPAN = (math.radians(145), math.radians(230))
PIN_ANG = math.radians(215)
CD = (Z_SECT + Z_PIN) * MOD / 2      # distancia entre ejes = 79.5
PIN_C = (CD * math.cos(PIN_ANG), CD * math.sin(PIN_ANG))

# trinquete + palanca
Q = (-42.0, 52.0)                    # eje del trinquete
L_END = (-88.0, 90.0)                # pomo de la palanca

# ejes y tornillería
D_PIVOT = 8.0      # eje principal Ø8 (rodamiento 608: 8x22x7)
D_608 = 22.0
D_PAWL = 5.0       # eje trinquete (tornillo de hombro M5)
D_PIN_SPRING = 4.0

# muelles metálicos (comprados): solo se modelan los pines y agujeros de enganche
OPEN_HOOK = (55.0, 16.3)   # agujero en el brazo de la pala móvil
OPEN_PIN = (-60.0, 125.0)  # pin en el tablero
STOP_PIN = (13.0, 73.9)     # tope de apertura (~45°): evita que el brazo choque con el trinquete
PAWL_HOOK_T = 0.6          # posición del agujero en la palanca (0=Q, 1=pomo)
PAWL_PIN = (-70.0, 118.0)

BOARD = (-130.0, 220.0, -120.0, 175.0)  # xmin, xmax, ymin, ymax
BOARD_T = 10.0

# ---------------- utilidades ----------------
def polar(r, a, c=(0.0, 0.0)):
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))

def prism(pts, z0, h):
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(h)

def band(c, r0, r1, a0, a1, z0, h, n=96):
    outer = [polar(r1, a0 + (a1 - a0) * i / n, c) for i in range(n + 1)]
    inner = [polar(r0, a1 - (a1 - a0) * i / n, c) for i in range(n + 1)]
    return prism(outer + inner, z0, h)

def disc(c, r, z0, h):
    return cq.Workplane("XY").workplane(offset=z0).center(*c).circle(r).extrude(h)

def slot_bar(p0, p1, w, z0, h):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy); ang = math.degrees(math.atan2(dy, dx))
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    return (cq.Workplane("XY").workplane(offset=z0).center(*mid)
            .transformed(rotate=(0, 0, ang)).slot2D(L + w, w).extrude(h))

def hole(solid, c, d, z0=-50, h=100):
    return solid.cut(disc(c, d / 2, z0, h))

def involute_tooth_pts(m, z, pa=20.0, n=8):
    """Perfil de evolvente de un diente centrado en el ángulo 0 (radios desde fondo a cabeza)."""
    rp = m * z / 2; rb = rp * math.cos(math.radians(pa)); ra = rp + m; rf = rp - 1.25 * m
    inv = lambda a: math.tan(a) - a
    ap = math.radians(pa)
    half = math.pi / (2 * z) + inv(ap) - BACKLASH / (2 * rp)   # semiancho angular en el círculo base (con juego)
    pts_r = []
    r_start = max(rb, rf)
    for i in range(n + 1):
        r = r_start + (ra - r_start) * i / n
        a = math.acos(rb / r) if r > rb else 0.0
        th = half - inv(a)
        pts_r.append((r, th))
    right = [(r * math.cos(-th), r * math.sin(-th)) for r, th in pts_r]
    left = [(r * math.cos(th), r * math.sin(th)) for r, th in reversed(pts_r)]
    return rf, right, left

def gear_pts(m, z, a_from=None, a_to=None, rot=0.0):
    """Puntos del contorno de un engranaje (completo o sector entre a_from y a_to)."""
    rf, right, left = involute_tooth_pts(m, z)
    st = 2 * math.pi / z
    ks = range(z) if a_from is None else range(math.ceil((a_from - rot) / st), math.floor((a_to - rot) / st) + 1)
    pts = []
    for k in ks:
        c = rot + k * st
        rc = lambda p: (p[0] * math.cos(c) - p[1] * math.sin(c), p[0] * math.sin(c) + p[1] * math.cos(c))
        pts.append(polar(rf, c - st / 2))
        pts += [rc(p) for p in right] + [rc(p) for p in left]
    if a_from is None:
        return pts
    return pts

# ---------------- piezas ----------------
# Tablero
board = (cq.Workplane("XY").workplane(offset=-BOARD_T)
         .center((BOARD[0] + BOARD[1]) / 2, (BOARD[2] + BOARD[3]) / 2)
         .rect(BOARD[1] - BOARD[0], BOARD[3] - BOARD[2]).extrude(BOARD_T))
board = hole(board, (0, 0), D_PIVOT - 0.2)
board = hole(board, Q, D_PAWL - 0.2)
board = hole(board, PIN_C, 22.5)                         # resalte del NEMA17
for dx in (-15.5, 15.5):
    for dy in (-15.5, 15.5):
        board = hole(board, (PIN_C[0] + dx, PIN_C[1] + dy), 3.4)  # M3 del NEMA17
for p in (OPEN_PIN, PAWL_PIN, STOP_PIN):
    board = hole(board, p, D_PIN_SPRING - 0.2)
STANDOFFS = [polar(57.0, math.radians(-120), C), polar(57.0, math.radians(-60), C)]
for p in STANDOFFS:
    board = hole(board, p, 4.3)

# Pala móvil + carraca + sector dentado (una sola pieza)
cm = C  # en posición cerrada comparte centro con la pala fija
mov = band(cm, R_SH0, R_SH1, ARC_MOV[0], ARC_MOV[1], ZA, T)
arm_end = polar((R_SH0 + R_SH1) / 2, ARC_MOV[1], cm)
mov = mov.union(slot_bar((0, 0), arm_end, ARM_W, ZA, T))
# rueda de carraca: r = RR + RH*frac((φ-90°)/paso)  -> bloquea el giro antihorario (apertura)
rat = []
a0 = math.pi / 2
for k in range(NT):
    s = a0 + k * PITCH
    rat.append(polar(RR, s))
    rat.append(polar(RR + RH, s + PITCH - 0.004))
mov = mov.union(prism(rat, ZA, T))
# sector: alma + dientes de evolvente
sect_rf = MOD * Z_SECT / 2 - 1.25 * MOD
web = band((0, 0), RR - 1, sect_rf - 0.3, SECT_SPAN[0], SECT_SPAN[1], ZA, T)
mov = mov.union(web)
st = 2 * math.pi / Z_SECT
SECT_PHASE = PIN_ANG - round(PIN_ANG / st) * st      # un diente del sector apunta al piñón en θ=0
rf, right, left = involute_tooth_pts(MOD, Z_SECT)
for k in range(math.ceil(SECT_SPAN[0] / st) + 1, math.floor(SECT_SPAN[1] / st)):
    c = k * st + SECT_PHASE
    rc = lambda p, c=c: (p[0] * math.cos(c) - p[1] * math.sin(c), p[0] * math.sin(c) + p[1] * math.cos(c))
    prof = [polar(rf - 0.8, c - st * 0.45)] + [rc(p) for p in right] + [rc(p) for p in left] + [polar(rf - 0.8, c + st * 0.45)]
    mov = mov.union(prism(prof, ZA, T))
# agujeros
mov = hole(mov, (0, 0), D_608)                       # rodamiento 608
mov = hole(mov, OPEN_HOOK, 4.0)                       # enganche del muelle de apertura
for i in range(4):                                     # aligeramientos
    mov = hole(mov, polar(24.0, math.radians(20 + 90 * i)), 9.0)

# Acolchados (EVA) – sólidos separados
pad_mov = band(cm, R_PAD0, R_SH0, ARC_MOV[0] + 0.04, ARC_MOV[1] - 0.04, ZA, T)
pad_fix = band(C, R_PAD0, R_SH0, ARC_FIX[0] + 0.04, ARC_FIX[1] - 0.04, ZB, T)

# Pala fija (capa B, encima) con apoyos al tablero
fix = band(C, R_SH0, R_SH1, ARC_FIX[0], ARC_FIX[1], ZB, T)
fix = fix.union(slot_bar((0, 0), polar((R_SH0 + R_SH1) / 2, ARC_FIX[0], C), ARM_W, ZB, T))
fix = fix.union(disc((0, 0), 14.0, ZB, T))
fix = hole(fix, (0, 0), D_PIVOT + 0.3)
for p in STANDOFFS:
    fix = hole(fix, p, 4.3)
standoffs = [disc(p, 4.0, 0, ZB).cut(disc(p, 2.15, -1, ZB + 2)) for p in STANDOFFS]

# Trinquete + palanca (una pieza)
tip_ang = math.pi / 2 + math.radians(2.0)
T_TIP = polar(RR + 0.8, tip_ang)
paw = slot_bar(Q, T_TIP, 8.0, ZA, T)
paw = paw.union(slot_bar(Q, L_END, 9.0, ZA, T))
paw = paw.union(disc(Q, 8.0, ZA, T))
paw = paw.union(disc(L_END, 10.0, ZA, T))
paw = paw.cut(disc((0, 0), RR + 0.3, ZA - 1, T + 2))        # recorta la punta al radio de fondo
paw = paw.cut(mov)                                            # la punta asienta exactamente en el hueco del diente
paw = hole(paw, Q, D_PAWL + 0.3)
hook = (Q[0] + (L_END[0] - Q[0]) * PAWL_HOOK_T, Q[1] + (L_END[1] - Q[1]) * PAWL_HOOK_T)
paw = hole(paw, hook, 3.5)

# Piñón del stepper (Ø5 con plano en D)
pin_pts = gear_pts(MOD, Z_PIN, rot=PIN_ANG + math.pi + math.pi / Z_PIN)   # hueco orientado al diente del sector
pin_pts = [(x + PIN_C[0], y + PIN_C[1]) for x, y in pin_pts]
pinion = prism(pin_pts, ZA, T)
bore = (cq.Workplane("XY").workplane(offset=ZA - 1).center(*PIN_C).circle(2.55).extrude(T + 2)
        .cut(cq.Workplane("XY").workplane(offset=ZA - 2).center(PIN_C[0] + 2.55 + 2.05, PIN_C[1]).rect(4.6, 8).extrude(T + 4)))
pinion = pinion.cut(bore)
pinion = pinion.union(disc(PIN_C, 7.0, ZA + T, 5.0).cut(disc(PIN_C, 2.55, ZA, 12)))   # buje

# NEMA17 detrás del tablero
NZ = -BOARD_T
nema = (cq.Workplane("XY").workplane(offset=NZ - 40).center(*PIN_C).rect(42.3, 42.3).extrude(40)
        .edges("|Z").chamfer(3.5))
nema = nema.union(disc(PIN_C, 11.0, NZ, 2.0).translate((0, 0, -2.0 + 0)))
shaft = disc(PIN_C, 2.5, NZ, ZA + T + 5 - NZ)

# Ejes y pines
pivot_shaft = disc((0, 0), D_PIVOT / 2, -BOARD_T, BOARD_T + ZB + T + 3)
pawl_shaft = disc(Q, D_PAWL / 2, -BOARD_T, BOARD_T + ZA + T + 2)
spring_pins = [disc(p, D_PIN_SPRING / 2, -BOARD_T, BOARD_T + ZB + T) for p in (OPEN_PIN, PAWL_PIN)]
stop_pin = disc(STOP_PIN, 3.0, -BOARD_T, BOARD_T + ZA + T + 2)
bearing = disc((0, 0), D_608 / 2, ZA, 7.0 - 1.0).cut(disc((0, 0), D_PIVOT / 2, ZA - 1, 9))

# Antebrazo de muestra (Ø84 de espuma), apoyado en la pala fija
arm_c = (C[0], C[1] - (R_PAD0 - 42.0))
forearm = disc(arm_c, 42.0, 0.0, ZB + T)

# ---------------- ensamblaje y exportación ----------------
asm = cq.Assembly(name="maqueta_carraca_5b")
col = lambda r, g, b, a=1.0: cq.Color(r, g, b, a)
asm.add(board, name="tablero", color=col(0.78, 0.66, 0.50))
asm.add(mov, name="pala_movil_carraca_sector", color=col(0.18, 0.43, 0.71))
asm.add(fix, name="pala_fija", color=col(0.75, 0.78, 0.82))
asm.add(pad_mov, name="acolchado_pala_movil", color=col(0.25, 0.29, 0.32))
asm.add(pad_fix, name="acolchado_pala_fija", color=col(0.25, 0.29, 0.32))
asm.add(paw, name="trinquete_palanca_QR", color=col(0.89, 0.44, 0.06))
asm.add(pinion, name="pinon_stepper", color=col(0.20, 0.22, 0.25))
asm.add(nema, name="NEMA17_referencia", color=col(0.15, 0.16, 0.18))
asm.add(shaft, name="eje_stepper_5mm", color=col(0.6, 0.62, 0.65))
asm.add(pivot_shaft, name="eje_pivote_8mm", color=col(0.6, 0.62, 0.65))
asm.add(bearing, name="rodamiento_608", color=col(0.6, 0.62, 0.65))
asm.add(pawl_shaft, name="eje_trinquete_M5", color=col(0.6, 0.62, 0.65))
for i, s in enumerate(standoffs):
    asm.add(s, name=f"separador_pala_fija_{i+1}", color=col(0.6, 0.62, 0.65))
asm.add(spring_pins[0], name="pin_muelle_apertura", color=col(0.18, 0.54, 0.41))
asm.add(spring_pins[1], name="pin_muelle_trinquete", color=col(0.18, 0.54, 0.41))
asm.add(stop_pin, name="pin_tope_apertura", color=col(0.6, 0.62, 0.65))
asm.add(forearm, name="antebrazo_muestra", color=col(0.91, 0.75, 0.63, 0.5))

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    asm.save(f"{out}/maqueta_carraca_5b.step")
    # piezas a fabricar por separado
    for name, part in [("pala_movil_carraca_sector", mov), ("pala_fija", fix),
                       ("trinquete_palanca_QR", paw), ("pinon_stepper", pinion)]:
        cq.exporters.export(part, f"{out}/{name}.stl")
    print("CD piñón-sector:", round(CD, 2), "mm  | centro piñón:", tuple(round(v, 2) for v in PIN_C))
