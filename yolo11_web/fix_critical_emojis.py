# -*- coding: utf-8 -*-
"""
快速修复关键文件中的 emoji 编码问题
"""

import os
import sys

# 强制使用 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 需要修复的文件列表
FILES_TO_FIX = [
    'yoloapp/flow/nine_node_with_tools.py',
    'yoloapp/tool/langchain_tools.py',
    'services/detection_service.py',
    'routers/agent_factory.py',
    'main.py',
]

# Emoji 替换映射（扩展版）
EMOJI_MAP = {
    '🚀': '[START]',
    '🎯': '[Node 1]',
    '📎': '[Node 2]',
    '🛠️': '[Node 4]',
    '🔍': '[Node 5]',
    '🔧': '[Node 6]',
    '✅': '[OK]',
    '❌': '[FAIL]',
    '⚠️': '[WARN]',
    '📊': '[STATS]',
    '🔑': '[KEY]',
    '💬': '[Node 9]',
    '❓': '[Node 7]',
    '📚': '[QUERY]',
    '🔬': '[DETECT]',
    '🌾': '[CROP]',
    '💧': '[WATER]',
    '☀️': '[WEATHER]',
    '🔄': '[PROGRESS]',
    '📦': '[BOX]',
    '🎯': '[TARGET]',
    '📍': '[LOCATION]',
    '💡': '[INFO]',
    '🚨': '[ALERT]',
    '🔔': '[NOTIFY]',
    '📈': '[CHART]',
    '🌡️': '[TEMP]',
    '🌧️': '[RAIN]',
    '🌤️': '[SUNNY]',
    '🌥️': '[CLOUDY]',
    '❄️': '[SNOW]',
    '🌪️': '[WIND]',
    '🌊': '[FLOOD]',
    '🔥': '[FIRE]',
    '⚡': '[LIGHTNING]',
    '🌈': '[RAINBOW]',
    '🌙': '[MOON]',
    '⭐': '[STAR]',
    '✨': '[SPARKLE]',
    '💫': '[DIZZY]',
    '🎉': '[PARTY]',
    '🎊': '[CONFETTI]',
    '🎈': '[BALLOON]',
    '🎁': '[GIFT]',
    '🏆': '[TROPHY]',
    '🥇': '[GOLD]',
    '🥈': '[SILVER]',
    '🥉': '[BRONZE]',
    '🏅': '[MEDAL]',
    '🎖️': '[MILITARY]',
    '🏵️': '[ROSETTE]',
    '🎗️': '[REMINDER]',
    '🎫': '[TICKET]',
    '🎟️': '[ADMISSION]',
    '🎪': '[CIRCUS]',
    '🎭': '[ARTS]',
    '🎨': '[ART]',
    '🎬': '[CLAPPER]',
    '🎤': '[MIC]',
    '🎧': '[HEADPHONE]',
    '🎼': '[SCORE]',
    '🎹': '[PIANO]',
    '🥁': '[DRUM]',
    '🎷': '[SAX]',
    '🎺': '[TRUMPET]',
    '🎸': '[GUITAR]',
    '🎻': '[VIOLIN]',
    '🎲': '[DICE]',
    '♟️': '[CHESS]',
    '🎯': '[DART]',
    '🎳': '[BOWLING]',
    '🎮': '[GAME]',
    '🎰': '[SLOT]',
    '🧩': '[PUZZLE]',
    '🚗': '[CAR]',
    '🚕': '[TAXI]',
    '🚙': '[SUV]',
    '🚌': '[BUS]',
    '🚎': '[TROLLEY]',
    '🏎️': '[RACE]',
    '🚓': '[POLICE]',
    '🚑': '[AMBULANCE]',
    '🚒': '[FIRE_TRUCK]',
    '🚐': '[VAN]',
    '🚚': '[TRUCK]',
    '🚛': '[SEMI]',
    '🚜': '[TRACTOR]',
    '🛴': '[SCOOTER]',
    '🛵': '[MOTOR]',
    '🏍️': '[MOTORCYCLE]',
    '🛺': '[AUTO]',
    '🚲': '[BIKE]',
    '🛴': '[KICK]',
    '🛹': '[SKATEBOARD]',
    '🛼': '[ROLLER]',
    '🚏': '[BUS_STOP]',
    '🛣️': '[MOTORWAY]',
    '🛤️': '[RAILWAY]',
    '🛢️': '[OIL]',
    '⛽': '[FUEL]',
    '🚨': '[SIREN]',
    '🚥': '[TRAFFIC]',
    '🚦': '[LIGHT]',
    '🛑': '[STOP]',
    '🚧': '[CONSTRUCTION]',
    '⚓': '[ANCHOR]',
    '⛵': '[SAILBOAT]',
    '🛶': '[CANOE]',
    '🚤': '[SPEEDBOAT]',
    '🛳️': '[SHIP]',
    '⛴️': '[FERRY]',
    '🛥️': '[MOTOR_BOAT]',
    '🚢': '[CRUISE]',
    '✈️': '[AIRPLANE]',
    '🛩️': '[SMALL_PLANE]',
    '🛫': '[DEPARTURE]',
    '🛬': '[ARRIVAL]',
    '🪂': '[PARACHUTE]',
    '💺': '[SEAT]',
    '🚁': '[HELICOPTER]',
    '🚟': '[SUSPENSION]',
    '🚠': '[MOUNTAIN]',
    '🚡': '[AERIAL]',
    '🛰️': '[SATELLITE]',
    '🚀': '[ROCKET]',
    '🛸': '[UFO]',
    '🛎️': '[BELLHOP]',
    '🧳': '[LUGGAGE]',
    '⌛': '[HOURGLASS]',
    '⏳': '[TIMER]',
    '⌚': '[WATCH]',
    '⏰': '[ALARM]',
    '⏱️': '[STOPWATCH]',
    '⏲️': '[TIMER_CLOCK]',
    '🕰️': '[MANTLE]',
    '🕛': '[TWELVE]',
    '🕧': '[TWELVE_THIRTY]',
    '🕐': '[ONE]',
    '🕜': '[ONE_THIRTY]',
    '🕑': '[TWO]',
    '🕝': '[TWO_THIRTY]',
    '🕒': '[THREE]',
    '🕞': '[THREE_THIRTY]',
    '🕓': '[FOUR]',
    '🕟': '[FOUR_THIRTY]',
    '🕔': '[FIVE]',
    '🕠': '[FIVE_THIRTY]',
    '🕕': '[SIX]',
    '🕡': '[SIX_THIRTY]',
    '🕖': '[SEVEN]',
    '🕢': '[SEVEN_THIRTY]',
    '🕗': '[EIGHT]',
    '🕣': '[EIGHT_THIRTY]',
    '🕘': '[NINE]',
    '🕤': '[NINE_THIRTY]',
    '🕙': '[TEN]',
    '🕥': '[TEN_THIRTY]',
    '🕚': '[ELEVEN]',
    '🕦': '[ELEVEN_THIRTY]',
    '🌑': '[NEW_MOON]',
    '🌒': '[WAXING_CRESCENT]',
    '🌓': '[FIRST_QUARTER]',
    '🌔': '[WAXING_GIBBOUS]',
    '🌕': '[FULL_MOON]',
    '🌖': '[WANING_GIBBOUS]',
    '🌗': '[LAST_QUARTER]',
    '🌘': '[WANING_CRESCENT]',
    '🌚': '[NEW_MOON_FACE]',
    '🌝': '[FULL_MOON_FACE]',
    '🌛': '[FIRST_QUARTER_FACE]',
    '🌜': '[LAST_QUARTER_FACE]',
    '🌞': '[SUN_FACE]',
    '☀️': '[SUN]',
    '🌟': '[GLOWING]',
    '🌠': '[SHOOTING]',
    '🌌': '[MILKY_WAY]',
    '☁️': '[CLOUD]',
    '⛅': '[PARTLY_CLOUDY]',
    '⛈️': '[THUNDER]',
    '🌤️': '[MOSTLY_SUNNY]',
    '🌥️': '[MOSTLY_CLOUDY]',
    '🌦️': '[PARTLY_SUNNY_RAIN]',
    '🌧️': '[RAIN_CLOUD]',
    '🌨️': '[SNOW_CLOUD]',
    '🌩️': '[LIGHTNING_CLOUD]',
    '🌪️': '[TORNADO]',
    '🌫️': '[FOG]',
    '🌬️': '[WIND_FACE]',
    '🌀': '[CYCLONE]',
    '🌈': '[RAINBOW]',
    '🌂': '[CLOSED_UMBRELLA]',
    '☂️': '[UMBRELLA]',
    '☔': '[UMBRELLA_RAIN]',
    '⛱️': '[BEACH_UMBRELLA]',
    '⚡': '[ZAP]',
    '❄️': '[SNOWFLAKE]',
    '☃️': '[SNOWMAN]',
    '⛄': '[SNOWMAN_NO_SNOW]',
    '☄️': '[COMET]',
    '🔥': '[FLAME]',
    '💧': '[DROPLET]',
    '🌊': '[WAVE]',
}

def fix_file(filepath):
    """修复单个文件"""
    try:
        if not os.path.exists(filepath):
            print(f"[SKIP] 文件不存在: {filepath}")
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 替换所有 emoji
        for emoji, replacement in EMOJI_MAP.items():
            content = content.replace(emoji, replacement)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] 已修复: {filepath}")
            return True
        else:
            print(f"[SKIP] 无需修复: {filepath}")
            return False
    
    except Exception as e:
        print(f"[FAIL] 修复失败 {filepath}: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("开始修复关键文件中的 emoji 编码问题...")
    print("=" * 60)
    
    fixed = 0
    for filepath in FILES_TO_FIX:
        if fix_file(filepath):
            fixed += 1
    
    print("\n" + "=" * 60)
    print(f"修复完成! 共修复 {fixed}/{len(FILES_TO_FIX)} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()
