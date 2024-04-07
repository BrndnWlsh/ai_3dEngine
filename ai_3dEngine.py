import numpy as np
import pygame
from pygame.locals import *

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Object Rendering")

# Initialize font
font = pygame.font.Font(None, 36)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (255, 255, 255)
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = True

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if self.active:
                if event.key == K_RETURN:
                    self.active = False
                elif event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

# Main loop
running = True
clock = pygame.time.Clock()

input_box = InputBox(250, 300, 300, 40)
input_entered = False
rotation_angle = 0

# Define cube vertices and faces
cube_vertices = np.array([
    [-1, -1, -1],
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, 1, 1]
])

cube_faces = [
    (0, 1, 2, 3),    # front face
    (1, 5, 6, 2),    # right face
    (4, 5, 6, 7),    # back face
    (0, 4, 7, 3),    # left face
    (0, 1, 5, 4),    # bottom face
    (2, 3, 7, 6)     # top face
]

# Define rotation matrix around specified axis
def rotation_matrix(theta, axis):
    axis = axis / np.linalg.norm(axis)
    a = np.cos(theta / 2)
    b, c, d = -axis * np.sin(theta / 2)
    return np.array([
        [a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (a * c + b * d)],
        [2 * (b * c + a * d), a * a - b * b + c * c - d * d, 2 * (c * d - a * b)],
        [2 * (b * d - a * c), 2 * (a * b + c * d), a * a - b * b - c * c + d * d]
    ])

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        input_box.handle_event(event)

    # Clear the screen
    SCREEN.fill((0, 0, 0))

    if input_box.active:
        # Prompt user for rotation axis vector
        vector_text = [
            font.render("Enter the rotation axis vector (comma-separated):", True, (255, 255, 255)),
            font.render("(e.g., '1,0,0' for [1, 0, 0]):", True, (255, 255, 255))
        ]
        SCREEN.blit(vector_text[0], (50, 200))
        SCREEN.blit(vector_text[1], (50, 230))

        # Update and draw input box
        input_box.update()
        input_box.draw(SCREEN)
    else:
        # Get rotation axis from input
        rotation_axis = None
        try:
            axis_input = input_box.text
            rotation_axis = np.array([float(x) for x in axis_input.split(',')])
            input_entered = True
        except ValueError:
            pass

        if input_entered:
            # Rotate the cube vertices around the specified axis
            rotation = rotation_matrix(rotation_angle, rotation_axis)
            rotated_vertices = np.dot(cube_vertices, rotation)

            # Project and render each face
            for face in cube_faces:
                face_vertices = [rotated_vertices[i] for i in face]
                face_vertices = np.array(face_vertices)

                # Project vertices
                projected_vertices = face_vertices.copy()
                z_offset = 5  # Offset to prevent division by zero
                projected_vertices[:, 2] += z_offset
                projected_vertices[:, :2] /= projected_vertices[:, 2].reshape(-1, 1)

                # Scale to screen
                projected_vertices[:, 0] = (projected_vertices[:, 0] + 1) * WIDTH / 2
                projected_vertices[:, 1] = (projected_vertices[:, 1] + 1) * HEIGHT / 2

                # Draw face
                pygame.draw.polygon(SCREEN, (255, 255, 255), projected_vertices[:, :2], 1)

            # Increment rotation angle
            rotation_angle += clock.tick() / 1000  # Get the time passed since the last frame

    pygame.display.flip()

pygame.quit()
