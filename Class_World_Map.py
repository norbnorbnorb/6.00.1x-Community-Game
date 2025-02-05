import random

import copy
from Class_Map import MapFloor


dungeons = [{'loc_str': f'enter cave {n}', 'amount': 1, 'char': 'C'} for n in range(1, 10)]
small_dungeon = {'tile_width': 4, 'tile_rows': 5, 'world_w': 2, 'world_r': 1}
test_events = [{'loc_str': f'events/default/rng', 'amount': 3, 'char': 'E'}]


class MapManager:
    def __init__(self, active_floor, dungeons, active_dungeon):
        self.active_floor = active_floor
        self.dungeons = dungeons
        self.active_dungeon = active_dungeon

    @classmethod
    def generate(cls):
        dungeons = [{'loc_str': f'enter cave {n}', 'amount': 1, 'char': 'C'} for n in range(1, 10)]
        small_dungeon = {'tile_width': 4, 'tile_rows': 5, 'world_w': 2, 'world_r': 1}
        test_events = [{'loc_str': f'events/default/rng', 'amount': 3, 'char': 'E'}]

        # init
        active_floor = 0
        dungeons = {'world_map': [MapFloor.generate('World Map', 1, dungeons, **small_dungeon)],
                    'cave 1': MapManager.make_new_dungeon('cave 1', [])}
        active_dungeon = dungeons['world_map']
        return cls(active_floor, dungeons, active_dungeon)

    @property
    def active_map(self):
        return self.active_dungeon[self.active_floor]

    def set_active_dungeon(self, dungeon):
        self.active_dungeon = dungeon

    @staticmethod
    def make_new_dungeon(dungeon_name, events, floors='rng'):
        lvl_down = {'loc_str': 'lvl_down', 'amount': 1, 'char': 'd'}
        lvl_up = {'loc_str': 'lvl_up', 'amount': 1, 'char': 'u'}
        world_map = {'loc_str': 'enter world_map', 'amount': 1, 'char': 'w'}
        events += test_events  # TODO: fix this!
        dungeon = []
        if floors == 'rng':
            floors = random.randint(0, 5)
        for f in range(1, floors + 1):
            # floor_events = []
            if f == 1:
                floor_events = [lvl_down, world_map]
            elif f == floors:
                floor_events = [world_map, lvl_up]
            else:
                floor_events = [lvl_down, lvl_up]
            dungeon.append(MapFloor.generate(dungeon_name, f, events+floor_events, **small_dungeon))
        return dungeon

    def enter_dungeon(self, event):
        dungeon_name = event[6:]  # remove 'Enter ' substring
        if dungeon_name not in self.dungeons.keys():
            self.dungeons[dungeon_name] = self.make_new_dungeon(dungeon_name, events=test_events)
        self.active_floor = 0
        self.set_active_dungeon(self.dungeons[dungeon_name])

    def set_floor(self, floor_num):
        self.active_floor += floor_num

    def run(self):
        while True:
            event = self.active_map.run_map()
            if event == 'lvl_up':
                if self.active_floor == 0:
                    self.enter_dungeon('enter world_map')
                else:
                    self.set_floor(-1)
                pass
            elif event == 'lvl_down':
                self.set_floor(1)
            elif event[:5] == 'enter':
                self.enter_dungeon(event)
            else:
                return event

    def serialize(self):
        dummy = copy.deepcopy(self.__dict__)
        for k, v in dummy['dungeons'].items():
            dummy['dungeons'][k] = [MapFloor.serialize(f) for f in v]
        dummy['active_dungeon'] = [dungeon.serialize() for dungeon in dummy['active_dungeon']]
        return dummy

    @classmethod
    def deserialize(cls, save_data):
        dummy = copy.deepcopy(save_data)
        for k, v in dummy['dungeons'].items():
            dummy['dungeons'][k] = [MapFloor.deserialize(f) for f in v]
        dummy['active_dungeon'] = [MapFloor.deserialize(*dummy['active_dungeon'])]
        return cls(**dummy)

    def __str__(self):
        return f'{self.active_dungeon}, {self.active_floor}'
# dungeon1 = {'loc_str': 'enter cave 1', 'amount': 1, 'char': 'd'}
