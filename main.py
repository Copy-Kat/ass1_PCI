
from collections.abc import Container
from enum import Enum, auto
import os

from typing import TYPE_CHECKING, List

from vi._static import _StaticSprite
from pygame.surface import Surface
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize

if TYPE_CHECKING:
    from typing_extensions import Self



@deserialize
@dataclass
class SingleSiteConfig(Config):

    site_color: tuple[int, int, int] = (152, 158, 153) 

    frame_count: int = 0 

    site_center: tuple[int, int] = (350, 350)




def sum_vec2(list: list[Vector2]) -> Vector2:
    result = Vector2(0, 0)
    for vec in list:
        result += vec
    return result

class Site():

    def __init__(self, x: int, y: int, color: tuple[int, int, int], radius: int):

        self.center = Vector2(x, y)
        self.color = color
        self.radius = radius
    

class Roach(Agent):
    config: SingleSiteConfig


    def change_position(self):

        self.there_is_no_escape()

        self.pos += self.move


class RoachSim(Simulation):
    config: SingleSiteConfig
    _sites: List[Site] = []

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self._running = False

        self.config.frame_count += 1
        print("Frame :", self.config.frame_count)


    def after_update(self):
        # Draw everything to the screen

        for site in self._sites:
            pg.draw.circle(self._screen, site.color, site.center, site.radius)

        self._all.draw(self._screen)


        if self.config.visualise_chunks:
            self.__visualise_chunks()

        # Update the screen with the new image
        pg.display.flip()

        self._clock.tick(self.config.fps_limit)

        current_fps = self._clock.get_fps()
        if current_fps > 0:
            self._metrics.fps._push(current_fps)

            if self.config.print_fps:
                print(f"FPS: {current_fps:.1f}")

config = SingleSiteConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )

x, y = config.window.as_tuple()

df = RoachSim(config).batch_spawn_agents(100, Roach, images=["images/bird.png"]).run().snapshots

file_name = "data.csv"

print(df)

#if not os.path.exists(file_name):
#    with open(file_name, 'w'): pass

# df.write_csv(file_name, separator=",")

print("Output: ", file_name)
