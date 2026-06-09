import cv2
import numpy as np

def scan_paper(image_path):

    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for cnt in contours:

        approx = cv2.approxPolyDP(
            cnt,
            0.02 * cv2.arcLength(cnt, True),
            True
        )

        if len(approx) == 4:

            pts = approx.reshape(4,2).astype(np.float32)

            # reorder points
            s = pts.sum(axis=1)
            diff = np.diff(pts, axis=1)

            rect = np.zeros((4,2), dtype="float32")

            rect[0] = pts[np.argmin(s)]     # top-left
            rect[3] = pts[np.argmax(s)]     # bottom-right
            rect[1] = pts[np.argmin(diff)]  # top-right
            rect[2] = pts[np.argmax(diff)]  # bottom-left

            # larger canvas to preserve full paper
            width, height = 1000, 1400

            dst = np.array([
                [0,0],
                [width,0],
                [0,height],
                [width,height]
            ], dtype=np.float32)

            matrix = cv2.getPerspectiveTransform(rect, dst)

            warp = cv2.warpPerspective(
                image,
                matrix,
                (width, height)
            )

            # preview warped paper
            cv2.imshow("Full Warped Paper", warp)
            cv2.waitKey(500)

            return warp

    return image