import cv2
import math
import numpy as np

cap = cv2.VideoCapture("./video1.mp4")
font = cv2.FONT_HERSHEY_DUPLEX

INF = 9999
YET = 0
width = 639
height = 359
centerX = 319

polygons = np.array([
        [(0, height-100), (width, height-100), (width-199, height-210), (199, height-210)]
    ])

def canny(image):
    blur = cv2.GaussianBlur(image,(5,5),0)
    canny = cv2.Canny(blur, 50, 200, None, 3)
    return canny

def region_of_interest(image, color):
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, color)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image

def red_filter(image):
    lower = np.array([0, 0, 200])
    upper = np.array([0, 0, 255])
    mask = cv2.inRange(image, lower, upper)
    out = cv2.bitwise_and(image, image, mask=mask)
    return out

def move(diretion, pwm=None):
    # 라즈베리파이 동작 구현
    print(diretion)

while True:
    ret, src = cap.read()
    src = cv2.resize(src, (width+1, height+1))

    dst = canny(src)
    masked_dst = region_of_interest(dst, (255, 255, 255))
    cdstP = cv2.cvtColor(masked_dst, cv2.COLOR_GRAY2BGR)

    masked_cdstP = region_of_interest(cdstP, (255, 255, 255))
    masked_src = region_of_interest(src, (255, 255, 255))

    linesP = cv2.HoughLinesP(masked_dst, 1, np.pi / 180, 50, None, minLineLength=50, maxLineGap=10)

    if linesP is not None:
        lLine = [YET, YET, YET, YET]
        rLine = [YET, YET, YET, YET]
        left_count = 0
        right_count = 0

        for i in range(0, len(linesP)):
            l = linesP[i][0]
            # l[0] : startX
            # l[1] : startY
            # l[2] : endX
            # l[3] : endY
            
            # 각도가 20<= deg <=160 일때만 출력
            grad = (l[3] - l[1]) / (l[2] - l[0])
            rad = math.atan(grad)
            deg = math.degrees(rad)
            deg = (deg + 360) % 180

            if deg>=90 and deg<=160:
                # left 차선 탐지
                lLine[0] = lLine[0] + l[0]
                lLine[1] = lLine[1] + l[1]
                lLine[2] = lLine[2] + l[2]
                lLine[3] = lLine[3] + l[3]
                left_count = left_count + 1
            elif deg>=20 and deg<=90:
                # right 차선 탐지
                rLine[0] = rLine[0] + l[0]
                rLine[1] = rLine[1] + l[1]
                rLine[2] = rLine[2] + l[2]
                rLine[3] = rLine[3] + l[3]
                right_count = right_count + 1

        # 배열의 저장된 모든 점의 평균값을 구함
        if left_count != 0:
            lLine[0] = lLine[0] / left_count
            lLine[1] = lLine[1] / left_count
            lLine[2] = lLine[2] / left_count
            lLine[3] = lLine[3] / left_count
        if right_count != 0:
            rLine[0] = rLine[0] / right_count
            rLine[1] = rLine[1] / right_count
            rLine[2] = rLine[2] / right_count
            rLine[3] = rLine[3] / right_count

        # left 평균 차선(Red) 출력
        cv2.line(masked_cdstP, (int(lLine[0]), int(lLine[1])),
                         (int(lLine[2]), int(lLine[3])), (0, 0, 255), 10, cv2.LINE_AA)
        # right 평균 차선(Red) 출력
        cv2.line(masked_cdstP, (int(rLine[0]), int(rLine[1])),
                     (int(rLine[2]), int(rLine[3])), (0, 0, 255), 10, cv2.LINE_AA)

        # 변환
        lStart = [int(lLine[0]), int(lLine[1])]
        lEnd = [int(lLine[2]), int(lLine[3])]
        rStart = [int(rLine[0]), int(rLine[1])]
        rEnd = [int(rLine[2]), int(rLine[3])]

    fm_cdstP = red_filter(masked_cdstP)

    # 차선 분석 기준선(Green) 출력
    cv2.line(src, (centerX-20, 0), (centerX-20, 359), (0, 255, 0), 1, cv2.LINE_AA)
    cv2.line(src, (centerX+20, 0), (centerX+20, 359), (0, 255, 0), 1, cv2.LINE_AA)
    cv2.line(fm_cdstP, (centerX-20, 0), (centerX-20, 359), (0, 255, 0), 1, cv2.LINE_AA)
    cv2.line(fm_cdstP, (centerX+20, 0), (centerX+20, 359), (0, 255, 0), 1, cv2.LINE_AA)

    lGrad = INF
    rGrad = INF
    if lStart[0]!=YET and rStart[0]!=YET:
        # left right 모두 차선 탐지가 된 경우
        if lStart[1] != lStart[0]:
            # 중앙선 침범이 아니라면
            lGrad = (lStart[1] - lEnd[1]) / (lStart[0] - lEnd[0])
        if rStart[1] != rStart[0]:
            # 중앙선 침범이 아니라면
            rGrad = (rStart[1] - rEnd[1]) / (rStart[0] - rEnd[0])

        # x절편, y절편, 교점
        l_yInter = lStart[1] - lGrad * lStart[0]
        r_yInter = rStart[1] - rGrad * rStart[0]
        l_xInter = (-1 * l_yInter) / lGrad
        r_xInter = (height - r_yInter) / rGrad
        crossX = (r_yInter - l_yInter) / (lGrad - rGrad)
        crossY = int(lGrad * crossX + l_yInter)

        if crossX < centerX-20:
            # 교점이 left 에 있을 때
            move("left")
            cv2.putText(fm_cdstP, "left", (centerX - 200, 80), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        elif crossX > centerX+20:
            # 교점이 right 에 있을 때
            move("right")
            cv2.putText(fm_cdstP, "right", (centerX + 80, 80), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        else:
            # 교점이 center 에 있을 때
            move("forward")
            cv2.putText(fm_cdstP, "forward", (centerX - 120, 340), font, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # left 연장선(Red) 출력
        cv2.line(fm_cdstP, (0, int(l_yInter)), (int(l_xInter), 0), (127, 127, 255), 1, cv2.LINE_AA)
        # right 연장선(Red) 출력
        cv2.line(fm_cdstP, (int((-1 * r_yInter) / rGrad), 0), (int(r_xInter), height),
                 (127, 127, 255), 1, cv2.LINE_AA)

        # 교점 출력
        if crossY>=0 and crossY<=height:
            cv2.circle(fm_cdstP, (int(crossX), crossY), 1, (255, 0, 0), 10)

    elif lStart[0]!=YET and rStart[0]==YET:
        # left 차선만 탐지된 경우
        move("only on right")
        cv2.putText(fm_cdstP, "right", (centerX + 80, 80), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
    elif lStart[0]==YET and rStart[0]!=YET:
        # right 차선만 탐지된 경우
        move("only on left")
        cv2.putText(fm_cdstP, "left", (centerX - 200, 80), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        # 둘다 탐지가 안된 경우
        move("forward")
        cv2.putText(fm_cdstP, "forward", (centerX - 120, 340), font, 2, (255, 255, 255), 2, cv2.LINE_AA)

    # 출력
    cv2.imshow("Source", src)
    cv2.imshow("Detected Lines (in red) - Probabilistic Line Transform", fm_cdstP)

    # 키보드 q가 눌리면 중단
    if cv2.waitKey(1)&0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()