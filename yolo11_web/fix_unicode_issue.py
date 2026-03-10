#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Unicode编码问题
由于Windows默认使用GBK编码，无法处理某些Unicode字符
"""

import os
import re
import sys


def fix_unicode_in_file(filepath):
    """修复文件中的Unicode字符"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 替换Unicode字符为ASCII替代
        replacements = {
            "[ERROR]": "[ERROR]",
            "[OK]": "[OK]",
            "[WARNING]": "[WARNING]",
            "[START]": "[START]",
            "[DETECT]": "[DETECT]",
            "[INFO]": "[INFO]",
            "[HOT]": "[HOT]",
            "[PACKAGE]": "[PACKAGE]",
            "[CELEBRATE]": "[CELEBRATE]",
            "[TARGET]": "[TARGET]",
            "[BOOK]": "[BOOK]",
            "[MAP]": "[MAP]",
            "[TOOL]": "[TOOL]",
            "[QUESTION]": "[QUESTION]",
            "[WAITING]": "[WAITING]",
            "[CHAT]": "[CHAT]",
            "[TIME]": "[TIME]",
            "[FOLDER]": "[FOLDER]",
            "[NOTE]": "[NOTE]",
            "[TIP]": "[TIP]",
            "[MICROSCOPE]": "[MICROSCOPE]",
            "[CHART]": "[CHART]",
            "[GRAPH_UP]": "[GRAPH_UP]",
            "[GRAPH_DOWN]": "[GRAPH_DOWN]",
            "[BELL]": "[BELL]",
            "[RED]": "[RED]",
            "[YELLOW]": "[YELLOW]",
            "[GREEN]": "[GREEN]",
            "[BLUE]": "[BLUE]",
            "[PURPLE]": "[PURPLE]",
            "[ORANGE]": "[ORANGE]",
            "[BLACK]": "[BLACK]",
            "[WHITE]": "[WHITE]",
            "[BROWN]": "[BROWN]",
            "[RED_SQUARE]": "[RED_SQUARE]",
            "[YELLOW_SQUARE]": "[YELLOW_SQUARE]",
            "[GREEN_SQUARE]": "[GREEN_SQUARE]",
            "[BLUE_SQUARE]": "[BLUE_SQUARE]",
            "[PURPLE_SQUARE]": "[PURPLE_SQUARE]",
            "[ORANGE_SQUARE]": "[ORANGE_SQUARE]",
            "[BLACK_SQUARE]": "[BLACK_SQUARE]",
            "[WHITE_SQUARE]": "[WHITE_SQUARE]",
            "[BROWN_SQUARE]": "[BROWN_SQUARE]",
            "[SMALL_DIAMOND]": "[SMALL_DIAMOND]",
            "[SMALL_BLUE_DIAMOND]": "[SMALL_BLUE_DIAMOND]",
            "[RED_TRIANGLE_UP]": "[RED_TRIANGLE_UP]",
            "[RED_TRIANGLE_DOWN]": "[RED_TRIANGLE_DOWN]",
            "[UP_TRIANGLE]": "[UP_TRIANGLE]",
            "[DOWN_TRIANGLE]": "[DOWN_TRIANGLE]",
            "[PLAY]": "[PLAY]",
            "[PAUSE]": "[PAUSE]",
            "[STOP]": "[STOP]",
            "[RECORD]": "[RECORD]",
            "[NEXT]": "[NEXT]",
            "[PREV]": "[PREV]",
            "[PLAY_PAUSE]": "[PLAY_PAUSE]",
            "[SHUFFLE]": "[SHUFFLE]",
            "[REPEAT]": "[REPEAT]",
            "[REPEAT_ONE]": "[REPEAT_ONE]",
            "[REFRESH]": "[REFRESH]",
            "[REFRESH_CW]": "[REFRESH_CW]",
            "[PIN]": "[PIN]",
            "[LOCATION]": "[LOCATION]",
            "[PAPERCLIP]": "[PAPERCLIP]",
            "[RULER]": "[RULER]",
            "[TRIANGLE_RULER]": "[TRIANGLE_RULER]",
            "[SCISSORS]": "[SCISSORS]",
            "[LINK]": "[LINK]",
            "[SATELLITE]": "[SATELLITE]",
            "[RADIO]": "[RADIO]",
            "[TV]": "[TV]",
            "[VIDEOTAPE]": "[VIDEOTAPE]",
            "[SPEAKER_HIGH_VOLUME]": "[SPEAKER]",
            "[LOUDSPEAKER]": "[MEGAPHONE]",
            "[MEGAPHONE]": "[CHEERING_MEGAPHONE]",
            "[BELL]": "[BELL]",
            "[POSTAL_HORN]": "[POSTAL_HORN]",
            "[MUSICAL_NOTE]": "[MUSICAL_NOTE]",
            "[MUSICAL_NOTES]": "[MUSICAL_NOTES]",
            "[MICROPHONE]": "[MICROPHONE]",
            "[LEVEL_SLIDER]": "[LEVEL_SLIDER]",
            "[CONTROL_KNOBS]": "[CONTROL_KNOBS]",
            "[MICROPHONE2]": "[MICROPHONE2]",
            "[HEADPHONES]": "[HEADPHONES]",
            "[MOBILE_PHONE]": "[MOBILE_PHONE]",
            "[MOBILE_PHONE_ARROW]": "[MOBILE_PHONE_ARROW]",
            "[TELEPHONE]": "[TELEPHONE]",
            "[TELEPHONE_RECEIVER]": "[TELEPHONE_RECEIVER]",
            "[PAGER]": "[PAGER]",
            "[FAX]": "[FAX]",
            "[BATTERY]": "[BATTERY]",
            "[ELECTRIC_PLUG]": "[ELECTRIC_PLUG]",
            "[LAPTOP]": "[LAPTOP]",
            "[DESKTOP]": "[DESKTOP]",
            "[PRINTER]": "[PRINTER]",
            "[KEYBOARD]": "[KEYBOARD]",
            "[MOUSE]": "[MOUSE]",
            "[TRACKBALL]": "[TRACKBALL]",
            "[MINIDISC]": "[MINIDISC]",
            "[FLOPPY_DISK]": "[FLOPPY_DISK]",
            "[CD]": "[CD]",
            "[DVD]": "[DVD]",
            "[ABACUS]": "[ABACUS]",
            "[CLAPPER_BOARD]": "[CLAPPER_BOARD]",
            "[VIDEO_GAME]": "[VIDEO_GAME]",
            "[JOYSTICK]": "[JOYSTICK]",
            "[DIE]": "[DIE]",
            "[CHESS_PAWN]": "[CHESS_PAWN]",
            "[TARGET]": "[TARGET]",
            "[BOWLING]": "[BOWLING]",
            "[SLOT_MACHINE]": "[SLOT_MACHINE]",
            "[BILLIARDS]": "[BILLIARDS]",
            "[CRYSTAL_BALL]": "[CRYSTAL_BALL]",
            "[NAZAR_AMULET]": "[NAZAR_AMULET]",
            "[ARTIST_PALETTE]": "[ARTIST_PALETTE]",
            "[THREAD]": "[THREAD]",
            "[YARN]": "[YARN]",
            "[GLASSES]": "[GLASSES]",
            "[SUNGLASSES]": "[SUNGLASSES]",
            "[GOGGLES]": "[GOGGLES]",
            "[LAB_COAT]": "[LAB_COAT]",
            "[SAFETY_VEST]": "[SAFETY_VEST]",
            "[NECKTIE]": "[NECKTIE]",
            "[T_SHIRT]": "[T_SHIRT]",
            "[JEANS]": "[JEANS]",
            "[SCARF]": "[SCARF]",
            "[GLOVES]": "[GLOVES]",
            "[COAT]": "[COAT]",
            "[SOCKS]": "[SOCKS]",
            "[DRESS]": "[DRESS]",
            "[KIMONO]": "[KIMONO]",
            "[SARI]": "[SARI]",
            "[ONE_PIECE_SWIMSUIT]": "[ONE_PIECE_SWIMSUIT]",
            "[BRIEFS]": "[BRIEFS]",
            "[SHORTS]": "[SHORTS]",
            "[BIKINI]": "[BIKINI]",
            "[WOMANS_CLOTHES]": "[WOMANS_CLOTHES]",
            "[PURSE]": "[PURSE]",
            "[HANDBAG]": "[HANDBAG]",
            "[CLUTCH_BAG]": "[CLUTCH_BAG]",
            "[BACKPACK]": "[BACKPACK]",
            "[MANS_SHOE]": "[MANS_SHOE]",
            "[ATHLETIC_SHOE]": "[ATHLETIC_SHOE]",
            "[HIKING_BOOT]": "[HIKING_BOOT]",
            "[FLAT_SHOE]": "[FLAT_SHOE]",
            "[HIGH_HEELED_SHOE]": "[HIGH_HEELED_SHOE]",
            "[WOMANS_SANDAL]": "[WOMANS_SANDAL]",
            "[BALLET_SHOES]": "[BALLET_SHOES]",
            "[WOMANS_BOOTS]": "[WOMANS_BOOTS]",
            "[CROWN]": "[CROWN]",
            "[WOMANS_HAT]": "[WOMANS_HAT]",
            "[TOP_HAT]": "[TOP_HAT]",
            "[GRADUATION_CAP]": "[GRADUATION_CAP]",
            "[BILLED_CAP]": "[BILLED_CAP]",
            "[RESCUE_WORKERS_HELMET]": "[RESCUE_WORKERS_HELMET]",
            "[PRAYER_BEADS]": "[PRAYER_BEADS]",
            "[LIPSTICK]": "[LIPSTICK]",
            "[RING]": "[RING]",
            "[GEM_STONE]": "[GEM_STONE]",
            "[MUTED_SPEAKER]": "[MUTED_SPEAKER]",
            "[SPEAKER_LOW_VOLUME]": "[SPEAKER_LOW_VOLUME]",
            "[SPEAKER_MEDIUM_VOLUME]": "[SPEAKER_MEDIUM_VOLUME]",
            "[SPEAKER_HIGH_VOLUME]": "[SPEAKER_HIGH_VOLUME]",
            "[LOUDSPEAKER]": "[LOUDSPEAKER]",
            "[MEGAPHONE]": "[MEGAPHONE]",
            "[POSTAL_HORN]": "[POSTAL_HORN]",
            "[BELL]": "[BELL]",
            "[BELL_WITH_SLASH]": "[BELL_WITH_SLASH]",
            "[MUSICAL_SCORE]": "[MUSICAL_SCORE]",
            "[MUSICAL_NOTE]": "[MUSICAL_NOTE]",
            "[MUSICAL_NOTES]": "[MUSICAL_NOTES]",
            "[MICROPHONE]": "[MICROPHONE]",
            "[LEVEL_SLIDER]": "[LEVEL_SLIDER]",
            "[CONTROL_KNOBS]": "[CONTROL_KNOBS]",
            "[MICROPHONE2]": "[MICROPHONE2]",
            "[HEADPHONES]": "[HEADPHONES]",
            "[RADIO]": "[RADIO]",
            "[SAXOPHONE]": "[SAXOPHONE]",
            "[GUITAR]": "[GUITAR]",
            "[MUSICAL_KEYBOARD]": "[MUSICAL_KEYBOARD]",
            "[TRUMPET]": "[TRUMPET]",
            "[VIOLIN]": "[VIOLIN]",
            "[BANJO]": "[BANJO]",
            "[DRUM]": "[DRUM]",
            "[LONG_DRUM]": "[LONG_DRUM]",
            "[MOBILE_PHONE]": "[MOBILE_PHONE]",
            "[MOBILE_PHONE_ARROW]": "[MOBILE_PHONE_ARROW]",
            "[TELEPHONE]": "[TELEPHONE]",
            "[TELEPHONE_RECEIVER]": "[TELEPHONE_RECEIVER]",
            "[PAGER]": "[PAGER]",
            "[FAX]": "[FAX]",
            "[BATTERY]": "[BATTERY]",
            "[ELECTRIC_PLUG]": "[ELECTRIC_PLUG]",
            "[LAPTOP]": "[LAPTOP]",
            "[DESKTOP]": "[DESKTOP]",
            "[PRINTER]": "[PRINTER]",
            "[KEYBOARD]": "[KEYBOARD]",
            "[MOUSE]": "[MOUSE]",
            "[TRACKBALL]": "[TRACKBALL]",
            "[MINIDISC]": "[MINIDISC]",
            "[FLOPPY_DISK]": "[FLOPPY_DISK]",
            "[CD]": "[CD]",
            "[DVD]": "[DVD]",
            "[ABACUS]": "[ABACUS]",
            "[CLAPPER_BOARD]": "[CLAPPER_BOARD]",
            "[VIDEO_GAME]": "[VIDEO_GAME]",
            "[JOYSTICK]": "[JOYSTICK]",
            "[DIE]": "[DIE]",
            "[CHESS_PAWN]": "[CHESS_PAWN]",
            "[TARGET]": "[TARGET]",
            "[BOWLING]": "[BOWLING]",
            "[SLOT_MACHINE]": "[SLOT_MACHINE]",
            "[BILLIARDS]": "[BILLIARDS]",
            "[CRYSTAL_BALL]": "[CRYSTAL_BALL]",
            "[NAZAR_AMULET]": "[NAZAR_AMULET]",
            "[ARTIST_PALETTE]": "[ARTIST_PALETTE]",
            "[THREAD]": "[THREAD]",
            "[YARN]": "[YARN]",
            "[GLASSES]": "[GLASSES]",
            "[SUNGLASSES]": "[SUNGLASSES]",
            "[GOGGLES]": "[GOGGLES]",
            "[LAB_COAT]": "[LAB_COAT]",
            "[SAFETY_VEST]": "[SAFETY_VEST]",
            "[NECKTIE]": "[NECKTIE]",
            "[T_SHIRT]": "[T_SHIRT]",
            "[JEANS]": "[JEANS]",
            "[SCARF]": "[SCARF]",
            "[GLOVES]": "[GLOVES]",
            "[COAT]": "[COAT]",
            "[SOCKS]": "[SOCKS]",
            "[DRESS]": "[DRESS]",
            "[KIMONO]": "[KIMONO]",
            "[SARI]": "[SARI]",
            "[ONE_PIECE_SWIMSUIT]": "[ONE_PIECE_SWIMSUIT]",
            "[BRIEFS]": "[BRIEFS]",
            "[SHORTS]": "[SHORTS]",
            "[BIKINI]": "[BIKINI]",
            "[WOMANS_CLOTHES]": "[WOMANS_CLOTHES]",
            "[PURSE]": "[PURSE]",
            "[HANDBAG]": "[HANDBAG]",
            "[CLUTCH_BAG]": "[CLUTCH_BAG]",
            "[BACKPACK]": "[BACKPACK]",
            "[MANS_SHOE]": "[MANS_SHOE]",
            "[ATHLETIC_SHOE]": "[ATHLETIC_SHOE]",
            "[HIKING_BOOT]": "[HIKING_BOOT]",
            "[FLAT_SHOE]": "[FLAT_SHOE]",
            "[HIGH_HEELED_SHOE]": "[HIGH_HEELED_SHOE]",
            "[WOMANS_SANDAL]": "[WOMANS_SANDAL]",
            "[BALLET_SHOES]": "[BALLET_SHOES]",
            "[WOMANS_BOOTS]": "[WOMANS_BOOTS]",
            "[CROWN]": "[CROWN]",
            "[WOMANS_HAT]": "[WOMANS_HAT]",
            "[TOP_HAT]": "[TOP_HAT]",
            "[GRADUATION_CAP]": "[GRADUATION_CAP]",
            "[BILLED_CAP]": "[BILLED_CAP]",
            "[RESCUE_WORKERS_HELMET]": "[RESCUE_WORKERS_HELMET]",
            "[PRAYER_BEADS]": "[PRAYER_BEADS]",
            "[LIPSTICK]": "[LIPSTICK]",
            "[RING]": "[RING]",
            "[GEM_STONE]": "[GEM_STONE]",
            "[MUTED_SPEAKER]": "[MUTED_SPEAKER]",
            "[SPEAKER_LOW_VOLUME]": "[SPEAKER_LOW_VOLUME]",
            "[SPEAKER_MEDIUM_VOLUME]": "[SPEAKER_MEDIUM_VOLUME]",
            "[SPEAKER_HIGH_VOLUME]": "[SPEAKER_HIGH_VOLUME]",
            "[LOUDSPEAKER]": "[LOUDSPEAKER]",
            "[MEGAPHONE]": "[MEGAPHONE]",
            "[POSTAL_HORN]": "[POSTAL_HORN]",
            "[BELL]": "[BELL]",
            "[BELL_WITH_SLASH]": "[BELL_WITH_SLASH]",
            "[MUSICAL_SCORE]": "[MUSICAL_SCORE]",
            "[MUSICAL_NOTE]": "[MUSICAL_NOTE]",
            "[MUSICAL_NOTES]": "[MUSICAL_NOTES]",
            "[MICROPHONE]": "[MICROPHONE]",
            "[LEVEL_SLIDER]": "[LEVEL_SLIDER]",
            "[CONTROL_KNOBS]": "[CONTROL_KNOBS]",
            "[MICROPHONE2]": "[MICROPHONE2]",
            "[HEADPHONES]": "[HEADPHONES]",
            "[RADIO]": "[RADIO]",
            "[SAXOPHONE]": "[SAXOPHONE]",
            "[GUITAR]": "[GUITAR]",
            "[MUSICAL_KEYBOARD]": "[MUSICAL_KEYBOARD]",
            "[TRUMPET]": "[TRUMPET]",
            "[VIOLIN]": "[VIOLIN]",
            "[BANJO]": "[BANJO]",
            "[DRUM]": "[DRUM]",
            "[LONG_DRUM]": "[LONG_DRUM]",
        }

        # 应用替换
        for unicode_char, ascii_replacement in replacements.items():
            content = content.replace(unicode_char, ascii_replacement)

        # 只在实际修改时写入文件
        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"修复: {filepath}")
            return True
        else:
            return False

    except Exception as e:
        print(f"修复 {filepath} 时出错: {e}")
        return False


def find_python_files():
    """查找所有Python文件"""
    python_files = []
    for root, dirs, files in os.walk("."):
        # 跳过某些目录
        dirs[:] = [
            d
            for d in dirs
            if d not in [".git", "__pycache__", "node_modules", ".venv", "venv"]
        ]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def main():
    print("开始修复Unicode编码问题...")
    print("=" * 50)

    python_files = find_python_files()
    print(f"找到 {len(python_files)} 个Python文件")

    fixed_count = 0
    for filepath in python_files:
        if fix_unicode_in_file(filepath):
            fixed_count += 1

    print("=" * 50)
    print(f"修复完成！共修复了 {fixed_count} 个文件")
    print("\n注意：")
    print("1. 已将Unicode表情符号替换为ASCII描述")
    print("2. 这可以避免Windows GBK编码环境下的问题")
    print("3. 建议使用UTF-8编码环境来避免此类问题")


if __name__ == "__main__":
    main()
