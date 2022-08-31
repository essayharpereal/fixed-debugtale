import enum
import binary


def to_fixed_point(f: float):
    return int(f * (2 ** 8))


class CutsceneCommands(enum.IntEnum):
    LOAD_SPRITE = 0  # Done (missing battle)
    PLAYER_CONTROL = 1  # Done
    WAIT_EXIT = 2  # Done (missing battle)
    WAIT_ENTER = 3  # Done (missing battle)
    SET_SHOWN = 4  # Done
    SET_ANIMATION = 5  # Done
    WAIT_FRAMES = 6  # Done
    SET_POS = 7  # Done
    MOVE_IN_FRAMES = 8  # Done
    START_DIALOGUE = 9  # Done
    WAIT_DIALOGUE_END = 10  # Done
    START_BATTLE = 11
    EXIT_BATTLE = 12
    START_BATTLE_DIALOGUE = 13
    BATTLE_ATTACK = 14
    WAIT_BATTLE_ATTACK = 15
    WAIT_BATTLE_ACTION = 16
    CMP_BATTLE_ACTION = 17
    CHECK_HIT = 18  # Done
    JUMP_IF = 19  # Done
    JUMP_IF_NOT = 20  # Done
    JUMP = 21  # Done
    MANUAL_CAMERA = 22  # Done
    UNLOAD_SPRITE = 23  # Done
    SCALE_IN_FRAMES = 24  # Done
    SET_SCALE = 25  # Done
    START_BGM = 26  # Done
    STOP_BGM = 27  # Done
    SET_POS_IN_FRAMES = 28  # Done
    DEBUG = 0xff  # Done


class TargetType(enum.IntEnum):
    NULL = 0
    PLAYER = 1
    SPRITE = 2
    CAMERA = 3


class Target:
    def __init__(self, target_type: int, target_id: int = 0):
        self.target_type: int = target_type
        self.target_id: int = target_id

    def write(self, wtr):
        wtr.write_uint8(self.target_type)
        if self.target_type == TargetType.SPRITE:
            wtr.write_uint8(self.target_id)


class Cutscene:
    def __init__(self, wtr: binary.BinaryWriter):
        self.wtr: binary.BinaryWriter = wtr
        self.version = 2
        self.file_size_pos = 0
        self.instructions_address = []
        self.pending_address = {}
        self.init_cutscene()

    def init_cutscene(self):
        self.wtr.write(b"CSCN")
        self.wtr.write_uint32(self.version)
        self.file_size_pos = self.wtr.tell()
        self.wtr.write_uint32(0)

    def end_cutscene(self):
        if len(self.pending_address) > 0:
            raise RuntimeError(f"Missing jump bind on instructions "
                               f"{', '.join([k for k in self.pending_address.keys()])}")
        size = self.wtr.tell()
        self.wtr.seek(self.file_size_pos)
        self.wtr.write_uint32(size)
        self.wtr.seek(size)
        self.wtr.close()

    def write_header(self, command_idx):
        self.instructions_address.append(self.wtr.tell())
        self.wtr.write_uint8(command_idx)

    def debug(self, string: str):
        self.write_header(CutsceneCommands.DEBUG)
        self.wtr.write_string(string, encoding="ascii")

    def load_sprite(self, x: float, y: float, sprite_path: str):
        self.write_header(CutsceneCommands.LOAD_SPRITE)
        self.wtr.write_int32(to_fixed_point(x))
        self.wtr.write_int32(to_fixed_point(y))
        self.wtr.write_string(sprite_path, encoding="ascii")

    def unload_sprite(self, room_sprite_id: int):
        self.write_header(CutsceneCommands.UNLOAD_SPRITE)
        self.wtr.write_uint8(room_sprite_id)

    def player_control(self, control: bool):
        self.write_header(CutsceneCommands.PLAYER_CONTROL)
        self.wtr.write_bool(control)

    def manual_camera(self, control: bool):
        self.write_header(CutsceneCommands.MANUAL_CAMERA)
        self.wtr.write_bool(control)

    def wait_exit(self):
        self.write_header(CutsceneCommands.WAIT_EXIT)

    def wait_enter(self):
        self.write_header(CutsceneCommands.WAIT_ENTER)

    def set_shown(self, target: Target, shown: bool):
        self.write_header(CutsceneCommands.SET_SHOWN)
        target.write(self.wtr)
        self.wtr.write_bool(shown)

    def set_animation(self, target: Target, animation: str):
        self.write_header(CutsceneCommands.SET_ANIMATION)
        target.write(self.wtr)
        self.wtr.write_string(animation, encoding="ascii")

    def wait_frames(self, frames: int):
        self.write_header(CutsceneCommands.WAIT_FRAMES)
        self.wtr.write_uint16(frames)

    # == NAVIGATION ==
    def set_pos(self, target: Target, x: float, y: float):
        self.write_header(CutsceneCommands.SET_POS)
        target.write(self.wtr)
        self.wtr.write_int32(to_fixed_point(x))
        self.wtr.write_int32(to_fixed_point(y))

    def set_scale(self, target: Target, x: float, y: float):
        self.write_header(CutsceneCommands.SET_SCALE)
        target.write(self.wtr)
        self.wtr.write_int32(to_fixed_point(x))
        self.wtr.write_int32(to_fixed_point(y))

    def set_pos_in_frames(self, target: Target, x: float, y: float, frames: int):
        self.write_header(CutsceneCommands.SET_POS_IN_FRAMES)
        target.write(self.wtr)
        self.wtr.write_int32(to_fixed_point(x))
        self.wtr.write_int32(to_fixed_point(y))
        self.wtr.write_uint16(frames)

    def move_in_frames(self, target: Target, dx: float, dy: float, frames: int):
        self.write_header(CutsceneCommands.MOVE_IN_FRAMES)
        target.write(self.wtr)
        dx = to_fixed_point(abs(dx)) * (1 if dx > 0 else -1)
        dy = to_fixed_point(abs(dy)) * (1 if dy > 0 else -1)
        self.wtr.write_int32(dx)
        self.wtr.write_int32(dy)
        self.wtr.write_uint16(frames)

    def scale_in_frames(self, target: Target, x: float, y: float, frames: int):
        self.write_header(CutsceneCommands.SCALE_IN_FRAMES)
        target.write(self.wtr)
        self.wtr.write_int32(to_fixed_point(x))
        self.wtr.write_int32(to_fixed_point(y))
        self.wtr.write_uint16(frames)

    # == DIALOGUE ==
    def start_dialogue(self, dialogue_text_id: int,
                       speaker_path: str, x: float, y: float,
                       idle_anim: str, talk_anim: str,
                       speaker_target: Target,
                       idle_anim2: str, talk_anim2: str,
                       font: str, frames_per_letter=4):
        self.write_header(CutsceneCommands.START_DIALOGUE)
        self.wtr.write_uint16(dialogue_text_id)
        self.wtr.write_string(speaker_path, encoding="ascii")
        self.wtr.write_int32(to_fixed_point(x))
        self.wtr.write_int32(to_fixed_point(y))
        self.wtr.write_string(idle_anim, encoding="ascii")
        self.wtr.write_string(talk_anim, encoding="ascii")
        speaker_target.write(self.wtr)
        self.wtr.write_string(idle_anim2, encoding="ascii")
        self.wtr.write_string(talk_anim2, encoding="ascii")
        self.wtr.write_string(font, encoding="ascii")
        self.wtr.write_uint16(frames_per_letter)

    def wait_dialogue_end(self):
        self.write_header(CutsceneCommands.WAIT_DIALOGUE_END)

    # == BATTLE ==
    def start_battle(self, enemies):
        self.write_header(CutsceneCommands.START_BATTLE)
        self.wtr.write_uint8(len(enemies))
        for enemy_id in enemies:
            self.wtr.write_uint16(enemy_id)

    def exit_battle(self):
        self.write_header(CutsceneCommands.EXIT_BATTLE)

    def start_battle_dialogue(self, x, y, dialogue_text_id,
                              speaker_target: Target, idle_anim: str,
                              talk_anim: str, duration: int):
        self.write_header(CutsceneCommands.START_BATTLE_DIALOGUE)
        self.wtr.write_int32(to_fixed_point(x))
        self.wtr.write_int32(to_fixed_point(y))
        self.wtr.write_uint16(dialogue_text_id)
        speaker_target.write(self.wtr)
        self.wtr.write_string(idle_anim, encoding="ascii")
        self.wtr.write_string(talk_anim, encoding="ascii")
        self.wtr.write_uint16(duration)

    def battle_attack(self, attack_pattern_id):
        self.write_header(CutsceneCommands.BATTLE_ATTACK)
        self.wtr.write_uint16(attack_pattern_id)

    def wait_battle_attack(self):
        self.write_header(CutsceneCommands.WAIT_BATTLE_ATTACK)

    def wait_battle_action(self, text_id, act_actions):
        self.write_header(CutsceneCommands.WAIT_BATTLE_ACTION)
        self.wtr.write_uint8(text_id)
        self.wtr.write_uint8(len(act_actions))
        for act_action in act_actions:
            self.wtr.write_uint8(act_action)

    def cmp_battle_action(self, compare_action):
        self.write_header(CutsceneCommands.CMP_BATTLE_ACTION)
        self.wtr.write_uint8(compare_action)

    def check_hit(self):
        self.write_header(CutsceneCommands.CHECK_HIT)

    # == LOGIC ==
    def jump_if(self):
        self.write_header(CutsceneCommands.JUMP_IF)
        self.pending_address[len(self.instructions_address) - 1] = self.wtr.tell()
        self.wtr.write_uint32(0)
        return len(self.instructions_address) - 1

    def jump_if_not(self):
        self.write_header(CutsceneCommands.JUMP_IF_NOT)
        self.pending_address[len(self.instructions_address) - 1] = self.wtr.tell()
        self.wtr.write_uint32(0)
        return len(self.instructions_address) - 1

    def jump(self):
        self.write_header(CutsceneCommands.JUMP)
        self.pending_address[len(self.instructions_address) - 1] = self.wtr.tell()
        self.wtr.write_uint32(0)
        return len(self.instructions_address) - 1

    def bind(self, jump_id):
        if jump_id in self.pending_address:
            pos = self.wtr.tell()
            self.wtr.seek(self.pending_address[jump_id])
            self.wtr.write_uint32(pos)
            self.wtr.seek(pos)
            del self.pending_address[jump_id]

    # == MUSIC ==
    def start_bgm(self, path: str, loop: bool):
        self.write_header(CutsceneCommands.START_BGM)
        self.wtr.write_bool(loop)
        self.wtr.write_string(path, encoding="ascii")

    def stop_bgm(self):
        self.write_header(CutsceneCommands.STOP_BGM)
