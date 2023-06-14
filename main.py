from enum import Enum, auto
#import os
from typing import Union

import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize

# All possible states of the agent
class States(Enum):
    WANDERING = auto(),
    JOIN = auto(),
    STILL = auto(),
    LEAVE = auto()

# Paramters to tweak, used by both configs
@deserialize
@dataclass
class Params(Config):

    join_timer: int = 10
    still_timer: int = 10
    leave_timer: int = 10
    random_change_angle_chance: float = 0.25            
    image_rotation: bool = True
    movement_speed: int = 1
    seed: int = 1

# 2 Config for 1/2 sites. Could be optimised but thats for later
@deserialize
@dataclass
class SingleSiteConfig(Params):

    site_center: Vector2 = Vector2(350, 350)
    site_color: tuple[int, int, int] =  (152, 152, 152)
    site_radius: int = 100

@deserialize
@dataclass
class DoubleSiteConfig(Params):

    site_centers: tuple[Vector2, Vector2] = (Vector2(350, 350), Vector2(250, 250))
    site_color: tuple[int, int, int] =  (152, 152, 152)
    site_radius: tuple[int, int] = (100, 50)


class Roach(Agent):
    config: Union[SingleSiteConfig, DoubleSiteConfig]
    site: int = -1
    state: States = States.WANDERING # init state as WANDERING
    join_timer: int
    still_timer: int
    leave_timer: int

    def change_position(self):

        self.there_is_no_escape()

        self.check_site() # check if agent in any sites

        self.save_data("site", self.site) # save data, could comment out

        # ------Wandering------

        if self.state == States.WANDERING:

            if self.on_site(): # if in a site then attempt to change state

                if self.join():
                    self.pos += self.move
                    self.state = States.JOIN
                    self.join_timer = self.config.join_timer # start JOIN timer
                    return
            
            # else continue random walk - code copy from source
            prng = self.shared.prng_move

            should_change_angle = prng.random()

            if self.config.random_change_angle_chance > should_change_angle:
                self.move.rotate(prng.uniform(-10, 10))

            self.pos += self.move

            return

        # ------Join------

        elif self.state == States.JOIN: # if in JOIN then just walk
            
            if self.join_timer > 0:
                self.pos += self.move
                self.join_timer -= 1
                return
            
            # stop and change to STILL when timer run out
            self.state = States.STILL
            self.still_timer = self.config.still_timer # start STILL timer
            return

        # ------Still------

        elif self.state == States.STILL: 
            
            # count down timer until next check
            if self.still_timer > 0:
                self.still_timer -= 1
                return

            if self.leave(): # attempt to leave
                self.pos += self.move
                self.state = States.LEAVE
                self.leave_timer = self.config.leave_timer # start LEAVE timer
                return
            
            # else reset STILL timer
            self.still_timer = self.config.still_timer

        # ------Leave------

        elif self.state == States.LEAVE:
            
            # walk until timer reach 0, take no consideration of any factors
            if self.leave_timer > 0:
                self.pos += self.move
                self.leave_timer -=1
                return

            self.state = States.WANDERING # change to WANDERING
            return
    
    # determine if agent want to join/leave or not
    def join(self) -> bool: 
        return True

    def leave(self) -> bool:
        return True
    
    # overrides on default function as we are using a different system
    def on_site(self) -> bool:
        return self.site != -1

    def on_site_id(self) -> int:
        return self.site

    def check_site(self):

        if isinstance(self.config, DoubleSiteConfig):
            for idx, center in enumerate(self.config.site_centers):
                if self.pos.distance_to(center) < self.config.site_radius[idx]:
                    self.site = idx
                    return

        elif self.pos.distance_to(self.config.site_center) < self.config.site_radius:
            self.site = 0
            return
        
        self.site = -1


class RoachSim(Simulation):
    config: Union[SingleSiteConfig, DoubleSiteConfig]

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    self._running = False

        
        print("Frame :", self.shared.counter)


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


config = SingleSiteConfig()

config1 = DoubleSiteConfig()

#x, y = config.window.as_tuple()

df = RoachSim(config1).batch_spawn_agents(100, Roach, images=["images/bird.png"]).run().snapshots

file_name = "data.csv"

print(df)

#if not os.path.exists(file_name):
#    with open(file_name, 'w'): pass

# df.write_csv(file_name, separator=",")

print("Output: ", file_name)
