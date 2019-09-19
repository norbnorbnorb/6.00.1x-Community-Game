import random

from Class_Map import MapFloor

dungeon1 = {'loc_str': 'enter cave 1', 'amount': 10, 'char': 'C'}
small_dungeon = {'tile_width': 3, 'tile_rows': 5, 'world_w': 2, 'world_r': 1, 'party_loc_x': 0, 'party_loc_y': 0}


class MapManager:
    def __init__(self):
        self.active_floor = 0
        self.dungeons = {'world_map': [MapFloor.generate('World Map', 1, [dungeon1], **small_dungeon)], 'cave 1': self.make_new_dungeon('cave 1', [])}
        self.active_dungeon = self.dungeons['world_map']

    @property
    def active_map(self):
        return self.active_dungeon[self.active_floor]

    def set_active_dungeon(self, dungeon):
        self.active_dungeon = dungeon

    def make_new_dungeon(self, dungeon_name, events, floors='rng'):
        lvl_down = {'loc_str': 'lvl_down', 'amount': 1, 'char': 'd'}
        lvl_up = {'loc_str': 'lvl_up', 'amount': 1, 'char': 'u'}
        world_map = {'loc_str': 'enter world_map', 'amount': 1, 'char': 'w'}

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
        dungeon_name = event[6:]
        if dungeon_name not in self.dungeons.keys():
            self.dungeons[dungeon_name] = self.make_new_dungeon(dungeon_name, events=[], floors=3)
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



# dungeon1 = {'loc_str': 'enter cave 1', 'amount': 1, 'char': 'd'}
