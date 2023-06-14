#from enum import Enum, auto
#import os
from typing import Union

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize

@deserialize
@dataclass
class SingleSiteConfig(Config):

    frame_count: int = 0

    site_center: Vector2 = Vector2(350, 350)

    site_color: tuple[int, int, int] =  (152, 152, 152)

    site_radius: int = 100

@deserialize
@dataclass
class DoubleSiteConfig(Config):

    frame_count: int = 0

    site_centers: tuple[Vector2, Vector2] = (Vector2(350, 350), Vector2(250, 250))

    site_color: tuple[int, int, int] =  (152, 152, 152)

    site_radius: tuple[int, int] = (100, 50)


class Roach(Agent):
    config: SingleSiteConfig

    def change_position(self):

        self.there_is_no_escape()

        self.pos += self.move


class RoachSim(Simulation):
    config: Union[SingleSiteConfig, DoubleSiteConfig]
    _sites: list[Site] = []

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self._running = False

        self.config.frame_count += 1
        print("Frame :", self.config.frame_count)


    def after_update(self):
        # Draw verything to the screen

        if type(self.config) is SingleSiteConfig:
            pg.draw.circle(self._screen, self.config.site_color, self.config.site_center, self.config.site_radius)

        if type(self.config) is DoubleSiteConfig:
            for idx, center in enumerate(self.config.site_centers):
                pg.draw.circle(self._screen, self.config.site_color, center, self.config.site_radius[idx])

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
            seed=1,
        )

config1 = DoubleSiteConfig(
            image_rotation=True,
            movement_speed=1,
            seed=1,
        )
x, y = config.window.as_tuple()

df = RoachSim(config1).batch_spawn_agents(100, Roach, images=["images/bird.png"]).run().snapshots

file_name = "data.csv"

print(df)

#if not os.path.exists(file_name):
#    with open(file_name, 'w'): pass

# df.write_csv(file_name, separator=",")

print("Output: ", file_name)
