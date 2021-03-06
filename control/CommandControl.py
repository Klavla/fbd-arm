import serial
import math
import time

u = 8.5
f = 6.5

shoulderPos = 90
forearmPos = 90
turntablePos = 0

useSerial = False

def gotoAngle(forearmAngle, shoulderAngle, turntableAngle):
    shoulderAngle = shoulderAngle * 180 / math.pi
    forearmAngle = forearmAngle * 180 / math.pi
    turntableAngle = turntableAngle * 180 / math.pi

    global shoulderPos
    global forearmPos
    global turntablePos

    deltaShoulder = shoulderAngle - shoulderPos
    shoulderPos = shoulderAngle
    deltaForearm = forearmAngle - forearmPos
    forearmPos = forearmAngle
    deltaTurntable = turntableAngle - turntablePos
    turntablePos = turntableAngle

    if(deltaForearm < 0):
        deltaForearm = 256 - (deltaForearm * -1)
    if(deltaShoulder < 0):
        deltaShoulder = 256 - (deltaShoulder * -1)
    if(deltaTurntable < 0):
        deltaTurntable = 256 - (deltaTurntable * -1)

    message = bytes([math.ceil(deltaForearm), math.ceil(deltaShoulder), math.ceil(deltaTurntable)])

    print("Deltas (Hex) " + message.hex())
    if useSerial:
        ser.write(message)
        print("wrote serial, received:")
        print(ser.read(3).hex())
    return

def gotoCoord(x, y, z):
    rawX = float(x)
    y = float(y)
    rawZ = float(z)
    x = math.sqrt((rawZ ** 2) + (rawX ** 2))

    w = math.sqrt((x ** 2) + (y ** 2))

    if(x < 0 or y < 0):
        print("Cannot go to negative x or y coords")
        return
    if(w <= f - u):
        print("Given coord is to close to base")
        return
    if(w >= f + u):
        print("Given coord is outside reach of arm")
        return
    if(math.sqrt(math.sqrt((x ** 2) + ((u - y) ** 2)) <= f)):
        print("Given coord cannot be reached without bending back")
        return

    wristAngle = math.atan(y / x)
    shoulderAngle = math.acos(((u ** 2) + (w ** 2) - (f ** 2)) / (2 * w * u)) + wristAngle
    forearmAngle = math.acos(((u ** 2) + (f ** 2) - (w ** 2)) / (2 * f * u))
    turntableAngle = math.atan2(rawX, rawZ)

    gotoAngle(shoulderAngle, forearmAngle, turntableAngle)
    return

while(True):
    command = input("\nEnter command: ")
    splitcommand = command.split(' ')

    if "exit" == splitcommand[0] or "quit" == splitcommand[0]:
        print("Goodbye")
        if useSerial:
            ser.close()
        exit()

    if "zero" == splitcommand[0]:
        shoulderPos = 90
        forearmPos = 90
        turntablePos = 0
        continue

    if "help" == splitcommand[0] or "h" == splitcommand[0]:
        print("Commands: r to send raw, a to send angles, and c to calculate angles for a given coord. Pass -h to any command for more specific help.")
        continue

    if "angle" == splitcommand[0]:
        if "h" in command:
            print("Pass in the desired shoulder angle, then the desired forearm angle, then the desired turntable angle. Uses degrees.")
            continue
        if len(splitcommand) < 4:
            print("Not enough arguments")
            continue
        gotoAngle(float(splitcommand[1]) * math.pi / 180,
            float(splitcommand[2]) * math.pi / 180,
            float(splitcommand[3]) * math.pi / 180)
        continue

    if "coord" == splitcommand[0]:
        if "h" in command:
            print("Pass in the desired X coord, then the desired Y coord, then the desired Z coord. Uses inches")
            continue
        if len(splitcommand) < 3:
            print("Not enough arguments")
            continue

        gotoCoord(splitcommand[1], splitcommand[2], splitcommand[3])
        continue

    if "2D circle" == splitcommand[0]:
        splitcommand[0] = "circleX"
        splitcommand.append(10)
        splitcommand.append(4)
        splitcommand.append(2)
        splitcommand.append(5)
        splitcommand.append(8)

    if "circleX" == splitcommand[0]:
        if "h" in command:
            print("xOffset, yOffset, radius, duration, resolution")
            continue
        xOffset = float(splitcommand[1])
        yOffset = float(splitcommand[2])
        radius = float(splitcommand[3])
        duration = float(splitcommand[4])
        resolution = int(splitcommand[5])
        for t in range(resolution):
            gotoCoord((math.cos(t * 2 * math.pi / resolution) * radius) + xOffset,
                (math.sin(t * 2 * math.pi / resolution) * radius) + yOffset, 0)
            time.sleep(duration / resolution)
        continue

    if "circle" == splitcommand[0]:
        splitcommand[0] = "circleZ"
        splitcommand.append(0)
        splitcommand.append(4)
        splitcommand.append(3)
        splitcommand.append(5)
        splitcommand.append(8)

    if "circleZ" == splitcommand[0]:
        if "h" in command:
            print("zOffset, yOffset, radius, duration, resolution")
            continue
        zOffset = float(splitcommand[1])
        yOffset = float(splitcommand[2])
        radius = float(splitcommand[3])
        duration = float(splitcommand[4])
        resolution = int(splitcommand[5])
        for t in range(resolution):
            gotoCoord(10,
                (math.sin(t * 2 * math.pi / resolution) * radius) + yOffset,
                (math.cos(t * 2 * math.pi / resolution) * radius) + zOffset)
            time.sleep(duration / resolution)
        continue

    if "serial" == splitcommand[0]:
        if "enable" in command:
            ser = serial.Serial('/dev/ttyACM0', 115200, write_timeout=5)
            useSerial = True
            continue
        if "disable" in command:
            ser.close()
            useSerial = False
            continue
        continue

    print("Unrecognized command try help for help")
