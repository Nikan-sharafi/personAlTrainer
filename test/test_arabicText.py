import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def draw_rounded_rect(img, rect_start, rect_end,
                      corner_width, box_color):
    x1, y1 = rect_start
    x2, y2 = rect_end
    w = corner_width
    # رسم مستطیل‌های توپر
    cv2.rectangle(img, (x1 + w, y1), (x2 - w, y1 + w), box_color, -1)
    cv2.rectangle(img, (x1 + w, y2 - w), (x2 - w, y2), box_color, -1)
    cv2.rectangle(img, (x1, y1 + w), (x1 + w, y2 - w), box_color, -1)
    cv2.rectangle(img, (x2 - w, y1 + w), (x2, y2 - w), box_color, -1)
    cv2.rectangle(img, (x1 + w, y1 + w), (x2 - w, y2 - w), box_color, -1)
    # رسم بیضی های توپر
    cv2.ellipse(img, (x1 + w, y1 + w), (w, w),
                angle=0, startAngle=-90, endAngle=-180,
                color=box_color, thickness=-1)
    cv2.ellipse(img, (x2 - w, y1 + w), (w, w),
                angle=0, startAngle=0, endAngle=-90,
                color=box_color, thickness=-1)
    cv2.ellipse(img, (x1 + w, y2 - w), (w, w),
                angle=0, startAngle=90, endAngle=180,
                color=box_color, thickness=-1)
    cv2.ellipse(img, (x2 - w, y2 - w), (w, w),
                angle=0, startAngle=0, endAngle=90,
                color=box_color, thickness=-1)
    return img

def main():
    img = cv2.imread('161.jpg')
    text = "طبیعت زیبای دوست داشتنی"
    text = 'aaaaaaaaaaaaaaaaaaaaaaaa'
    pos = (20,10)
    x, y = pos
    offset = (20,10)
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                   1, 1)
    text_w, text_h = text_size
    rec_start = tuple(p - o for p, o in zip(pos, offset))
    rec_end = tuple(m + n - o for m, n, o in
                    zip((x + text_w, y + text_h), offset, (25, 0)))
    print(text_size )
    print(rec_start)
    print(rec_end)
    img = draw_rounded_rect(img, rec_start,
                            rec_end, 8,
                            (255,255,0))
    cv2.imshow('frame',img)
    cv2.waitKey(0)
    image = Image.open( "161.jpg")
    font = ImageFont.truetype(
        'Vazir.ttf'
    )
    canvas = ImageDraw.Draw(image)
    canvas.text((100, 0), text, (0, 0, 0), font=font, direction="rtl")
    image.save("result.jpg")

if __name__ == '__main__':
    main()