import math
import random
import sys
import pygame

pygame.init()

# ---------------- SETTINGS ----------------
WIDTH, HEIGHT = 1000, 750
PARTICLE_COUNT = 3000
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("3D Particle Heart | Interactive")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 17)
small_font = pygame.font.SysFont("consolas", 14)

# ---------------- COLORS ----------------
BLACK = (3, 2, 12)
RED = (255, 25, 75)
PINK = (255, 100, 160)
WHITE_PINK = (255, 190, 220)

# ---------------- HEART GENERATION ----------------
def heart_boundary(t):
    """Classic mathematical heart outline."""
    x = 16 * math.sin(t) ** 3
    y = (
        13 * math.cos(t)
        - 5 * math.cos(2 * t)
        - 2 * math.cos(3 * t)
        - math.cos(4 * t)
    )
    return x, y


def create_particles():
    result = []

    for i in range(PARTICLE_COUNT):
        # Fill the interior by scaling a point on the heart boundary.
        t = random.uniform(0, math.tau)
        radius = math.sqrt(random.random())

        bx, by = heart_boundary(t)

        x = bx * radius
        y = by * radius
        z = random.uniform(-4.5, 4.5)

        result.append({
            "x": x,
            "y": y,
            "z": z,
            "size": random.choices([1, 2, 3], [4, 5, 1])[0],
            "phase": random.uniform(0, math.tau),
            "brightness": random.uniform(0.65, 1.0),
            "start_x": random.uniform(-40, 40),
            "start_y": random.uniform(-35, 35),
            "start_z": random.uniform(-25, 25),
        })

    return result


particles = create_particles()

# ---------------- CAMERA ----------------
rotation_y = 0.0
rotation_x = 0.0

zoom = 1.0
MIN_ZOOM = 0.45
MAX_ZOOM = 4.0

pan_x = 0.0
pan_y = 0.0

auto_rotate = True
dragging = False
show_help = True

last_mouse_x = 0
last_mouse_y = 0

start_time = pygame.time.get_ticks() / 1000.0

# Background stars
stars = [
    (
        random.randrange(WIDTH),
        random.randrange(HEIGHT),
        random.choice([1, 1, 1, 2]),
        random.uniform(0.4, 1.0),
    )
    for _ in range(220)
]

# ---------------- 3D PROJECTION ----------------
def project(x, y, z, center_x, center_y, scale):
    global rotation_x, rotation_y, pan_x, pan_y

    # Rotate around vertical axis.
    rx = x * math.cos(rotation_y) + z * math.sin(rotation_y)
    rz = -x * math.sin(rotation_y) + z * math.cos(rotation_y)

    # Rotate around horizontal axis.
    ry = y * math.cos(rotation_x) - rz * math.sin(rotation_x)
    rz2 = y * math.sin(rotation_x) + rz * math.cos(rotation_x)

    # Perspective projection.
    depth = max(150.0, 500.0 + rz2 * 4.0)
    perspective = 500.0 / depth

    px = center_x + pan_x + rx * scale * perspective
    py = center_y + pan_y - ry * scale * perspective

    return int(px), int(py), perspective, rz2


# ---------------- ZOOM TOWARD CURSOR ----------------
def zoom_at(mouse_x, mouse_y, factor, center_x, center_y):
    global zoom, pan_x, pan_y

    old_zoom = zoom
    new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom * factor))

    if new_zoom == old_zoom:
        return

    ratio = new_zoom / old_zoom

    # Keep the point beneath the cursor approximately fixed.
    relative_x = mouse_x - center_x - pan_x
    relative_y = mouse_y - center_y - pan_y

    pan_x = mouse_x - center_x - relative_x * ratio
    pan_y = mouse_y - center_y - relative_y * ratio

    zoom = new_zoom


# ---------------- RESET ----------------
def reset_camera():
    global rotation_x, rotation_y, zoom, pan_x, pan_y

    rotation_x = 0.0
    rotation_y = 0.0
    zoom = 1.0
    pan_x = 0.0
    pan_y = 0.0


# ---------------- MAIN LOOP ----------------
running = True

while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.04)
    elapsed = pygame.time.get_ticks() / 1000.0 - start_time

    width, height = screen.get_size()
    center_x = width // 2
    center_y = height // 2

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_SPACE:
                auto_rotate = not auto_rotate

            elif event.key == pygame.K_h:
                show_help = not show_help

            elif event.key == pygame.K_r:
                particles = create_particles()
                start_time = pygame.time.get_ticks() / 1000.0
                reset_camera()

            elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                zoom_at(center_x, center_y, 1.15, center_x, center_y)

            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                zoom_at(center_x, center_y, 1 / 1.15, center_x, center_y)

            elif event.key == pygame.K_LEFT:
                rotation_y -= 0.12

            elif event.key == pygame.K_RIGHT:
                rotation_y += 0.12

            elif event.key == pygame.K_UP:
                rotation_x += 0.12

            elif event.key == pygame.K_DOWN:
                rotation_x -= 0.12

        # Start rotation by holding the LEFT mouse button.
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                dragging = True
                last_mouse_x, last_mouse_y = event.pos

            # Mouse wheel up: zoom in.
            elif event.button == 4:
                zoom_at(
                    event.pos[0], event.pos[1],
                    1.15, center_x, center_y
                )

            # Mouse wheel down: zoom out.
            elif event.button == 5:
                zoom_at(
                    event.pos[0], event.pos[1],
                    1 / 1.15, center_x, center_y
                )

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION:

            if dragging:
                mx, my = event.pos

                dx = mx - last_mouse_x
                dy = my - last_mouse_y

                rotation_y += dx * 0.009
                rotation_x += dy * 0.009

                # Avoid extreme flipping.
                rotation_x = max(-1.5, min(1.5, rotation_x))

                last_mouse_x = mx
                last_mouse_y = my

        # Newer Pygame versions support this event.
        elif event.type == pygame.MOUSEWHEEL:

            mx, my = pygame.mouse.get_pos()

            if event.y > 0:
                zoom_at(mx, my, 1.15 ** event.y, center_x, center_y)
            elif event.y < 0:
                zoom_at(mx, my, 1.15 ** event.y, center_x, center_y)

    # ---------------- ANIMATION ----------------
    if auto_rotate and not dragging:
        rotation_y += dt * 0.22

    screen.fill(BLACK)

    # Draw background stars.
    for sx, sy, size, brightness in stars:
        twinkle = 0.65 + 0.35 * math.sin(elapsed * 1.5 + sx)
        shade = int(75 * brightness * twinkle)

        pygame.draw.circle(
            screen,
            (shade, shade // 2, min(130, shade + 30)),
            (sx % width, sy % height),
            size,
        )

    # Smooth gathering animation.
    gather = min(1.0, elapsed / 2.5)
    gather = gather * gather * (3 - 2 * gather)

    # Heartbeat pulse.
    pulse = (
        1.0
        + 0.035 * math.sin(elapsed * 3.0)
        + 0.012 * math.sin(elapsed * 6.0)
    )

    base_scale = min(width / 43.0, height / 41.0)
    scale = base_scale * zoom * pulse

    # ---------------- PARTICLES ----------------
    projected_particles = []

    for p in particles:

        # Move particles from scattered positions into the heart.
        x = p["start_x"] * (1 - gather) + p["x"] * gather
        y = p["start_y"] * (1 - gather) + p["y"] * gather
        z = p["start_z"] * (1 - gather) + p["z"] * gather

        # Gentle movement.
        x += math.sin(elapsed * 1.5 + p["phase"]) * 0.08 * gather
        y += math.cos(elapsed * 1.7 + p["phase"]) * 0.08 * gather

        px, py, perspective, depth = project(
            x, y, z, center_x, center_y, scale
        )

        twinkle = 0.70 + 0.30 * math.sin(
            elapsed * 4.0 + p["phase"]
        )

        size = max(1, int(p["size"] * perspective))
        brightness = p["brightness"] * twinkle

        projected_particles.append(
            (depth, px, py, size, brightness, p["phase"])
        )

    # Back-to-front rendering.
    projected_particles.sort(key=lambda item: item[0])

    for depth, px, py, size, brightness, phase in projected_particles:

        if not (-15 <= px < width + 15 and -15 <= py < height + 15):
            continue

        shade = 0.5 + 0.5 * math.sin(phase + elapsed)

        red = 255
        green = int((20 + 75 * shade) * brightness)
        blue = int((55 + 120 * shade) * brightness)

        color = (
            red,
            max(0, min(255, green)),
            max(0, min(255, blue)),
        )

        # Glow around brighter particles.
        if size >= 2:
            pygame.draw.circle(
                screen,
                (100, 8, 35),
                (px, py),
                size + 2,
            )

        pygame.draw.circle(screen, color, (px, py), size)

        # Occasional tiny white-pink spark.
        if brightness > 0.9 and random.random() < 0.008:
            pygame.draw.circle(
                screen,
                WHITE_PINK,
                (px, py),
                1,
            )

    # ---------------- INTERFACE ----------------
    title = font.render(
        "3D PARTICLE HEART",
        True,
        PINK,
    )
    screen.blit(title, (18, 15))

    if show_help:
        instructions = [
            "Hold LEFT mouse button + drag: Rotate",
            "Mouse wheel: Zoom toward cursor",
            "Arrow keys: Rotate",
            "+ / - keys: Zoom",
            "SPACE: Toggle auto-rotation",
            "R: Reset camera and particles",
            "H: Hide/show help",
            "ESC: Exit",
        ]

        for i, line in enumerate(instructions):
            label = small_font.render(
                line,
                True,
                (190, 180, 205),
            )
            screen.blit(label, (18, 43 + i * 21))

    zoom_label = small_font.render(
        f"Zoom: {zoom:.2f}x",
        True,
        (255, 130, 175),
    )
    screen.blit(zoom_label, (18, height - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()